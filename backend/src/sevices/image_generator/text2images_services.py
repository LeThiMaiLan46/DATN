import torch
import numpy as np
from transformers import AutoConfig, AutoModelForCausalLM
from janus.models import MultiModalityCausalLM, VLChatProcessor
from PIL import Image

class Text_to_Images():
    def __init__(self, path_model):
        self.config = AutoConfig.from_pretrained(path_model)
        self.language_config = self.config.language_config
        self.language_config._attn_implementation = 'eager'
        self.vl_gpt = AutoModelForCausalLM.from_pretrained(path_model,
                                                    language_config=self.language_config,
                                                    trust_remote_code=True)
        self.vl_gpt = self.vl_gpt.to(torch.bfloat16).cuda()
        self.vl_chat_processor = VLChatProcessor.from_pretrained(path_model)
        self.tokenizer = self.vl_chat_processor.tokenizer
        self.cuda_device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def unpack(self, dec, width, height, parallel_size=1):
        dec = dec.to(torch.float32).cpu().numpy().transpose(0, 2, 3, 1)
        dec = np.clip((dec + 1) / 2 * 255, 0, 255)

        visual_img = np.zeros((parallel_size, width, height, 3), dtype=np.uint8)
        visual_img[:, :, :] = dec

        return visual_img
        
    def generate(self,
             input_ids,
             width,
             height,
             temperature: float = 1,
             parallel_size: int = 1,
             cfg_weight: float = 5,
             image_token_num_per_image: int = 576,
             patch_size: int = 16):
        torch.cuda.empty_cache()
        tokens = torch.zeros((parallel_size * 2, len(input_ids)), dtype=torch.int).to(self.cuda_device)
        for i in range(parallel_size * 2):
            tokens[i, :] = input_ids
            if i % 2 != 0:
                tokens[i, 1:-1] = self.vl_chat_processor.pad_id
        inputs_embeds = self.vl_gpt.language_model.get_input_embeddings()(tokens)
        generated_tokens = torch.zeros((parallel_size, image_token_num_per_image), dtype=torch.int).to(self.cuda_device)

        pkv = None
        for i in range(image_token_num_per_image):
            outputs = self.vl_gpt.language_model.model(inputs_embeds=inputs_embeds, use_cache=True, past_key_values=pkv)
            pkv = outputs.past_key_values
            hidden_states = outputs.last_hidden_state
            logits = self.vl_gpt.gen_head(hidden_states[:, -1, :])
            logit_cond = logits[0::2, :]
            logit_uncond = logits[1::2, :]
            logits = logit_uncond + cfg_weight * (logit_cond - logit_uncond)
            probs = torch.softmax(logits / temperature, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            generated_tokens[:, i] = next_token.squeeze(dim=-1)
            next_token = torch.cat([next_token.unsqueeze(dim=1), next_token.unsqueeze(dim=1)], dim=1).view(-1)
            img_embeds = self.vl_gpt.prepare_gen_img_embeds(next_token)
            inputs_embeds = img_embeds.unsqueeze(dim=1)
            patches = self.vl_gpt.gen_vision_model.decode_code(
            generated_tokens.to(dtype=torch.int), 
            shape=[parallel_size, 8, width // patch_size, height // patch_size]
        )

        return generated_tokens.to(dtype=torch.int), patches

    def generate_image(self, prompt, seed, guidance):
        torch.cuda.empty_cache()
        seed = seed if seed is not None else 12345
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        np.random.seed(seed)
        width = 384
        height = 384
        parallel_size = 1
        
        with torch.no_grad():
            messages = [{'role': 'User', 'content': prompt}, {'role': 'Assistant', 'content': ''}]
            text = self.vl_chat_processor.apply_sft_template_for_multi_turn_prompts(
                conversations=messages,
                sft_format=self.vl_chat_processor.sft_format,
                system_prompt=''
            )
            text = text + self.vl_chat_processor.image_start_tag
            input_ids = torch.LongTensor(self.tokenizer.encode(text))
            _, patches = self.generate(input_ids, width // 16 * 16, height // 16 * 16, cfg_weight=guidance, parallel_size=parallel_size)
            images = self.unpack(patches, width // 16 * 16, height // 16 * 16)

            return [Image.fromarray(images[i]).resize((1024, 1024), Image.LANCZOS) for i in range(parallel_size)]