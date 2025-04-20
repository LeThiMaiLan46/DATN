import os
import time
import torch
import logging
import torchaudio
import queue
import threading
import json
import re
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from io import BytesIO
from vinorm import TTSnorm
from src.sevices.kokoro_pipeline import KPipeline
from src.sevices.kokoro_pipeline.model import KModel
from transformers import VitsModel, AutoTokenizer


from src.utils.text_split import split_by_char_limit_multilingual

class TTS_Services():
    def __init__(self, path_model,path_config ):
        self.config = XttsConfig()
        self.config.load_json(path_config)
        self.model = Xtts.init_from_config(self.config)
        self.model.load_checkpoint(self.config, checkpoint_dir=path_model, use_deepspeed=False)
        self.model.cuda()
        logging.info('Load model Text to Speech successfully! ......')
        self.num_worker_threads = 4
        self.lang_support  = ['ar', 'zh-cn', 'cs', 'nl', 'en', 'fr', 'de', 'hi', 'hu', 'it', 'ja', 'ko', 'pl', 'pt', 'ru', 'es', 'tr']

        
    
    def tts_process(self,text:str, language:str):
        chunks = split_by_char_limit_multilingual(text=text, lang=language)
        
        return chunks
    
    def transcrition(self,text,language):
        chunks = self.model.inference_stream(
            text,
            language,
            self.gpt_cond_latent,
            self.speaker_embedding
        )
        return chunks
    
    async def tts_transcribable(self, text: str, language: str, path_audio_style:str):
        self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(audio_path=[path_audio_style]) 

        wav_chunks_total = []
        text_chunks = self.tts_process(text,language)

        for index,sentences in enumerate(text_chunks):
            wav_chunks = self.transcrition(sentences,language)
            for index, wav in enumerate(wav_chunks):
                wav_chunks_total.append(wav)
                
        wav_file = torch.cat(wav_chunks_total, dim=0)
        wav_io = BytesIO()
        torchaudio.save(wav_io, wav_file.squeeze().unsqueeze(0).cpu(), 22500, format="wav")
        wav_io.seek(0)
        return wav_io
    
    
class TTS_Vi_Services():
    def __init__(self, path_model,path_config ):
        self.config = XttsConfig()
        self.config.load_json(path_config)
        self.model = Xtts.init_from_config(self.config)
        self.model.load_checkpoint(self.config, checkpoint_dir=path_model, use_deepspeed=True)
        self.model.cuda()
        logging.info('Load model Text to Speech successfully! ......')
        self.num_worker_threads = 4
        
    
    def tts_process(self,text:str, language:str):
        chunks = split_by_char_limit_multilingual(text=text, lang=language)
        
        return chunks
    def normalize_vietnamese_text(self,text):
        new_text = (
            TTSnorm(text, unknown=False, lower=False, rule=True)
            .replace("..", ".")
            .replace("!.", "!")
            .replace("?.", "?")
            .replace(" .", ".")
            .replace(" ,", ",")
            .replace('"', "")
            .replace("'", "")
            .replace("AI", "Ây Ai")
            .replace("A.I", "Ây Ai")
        )
        return new_text
    
    def transcrition(self,text,language):
        text = self.normalize_vietnamese_text(text)
        chunks = self.model.inference(
            text,
            language,
            self.gpt_cond_latent,
            self.speaker_embedding,
            temperature=0.3,
            length_penalty=1.0,
            repetition_penalty=10.0,
            top_k=30,
            top_p=0.85,
            enable_text_splitting=True
        )
        return chunks
    
    async def tts_transcribable(
        self, 
        text: str, 
        language: str, 
        path_audio_style: str
    ) -> BytesIO:
        """
        Convert text to speech with transcription support.
        
        :param text: Input text to be converted to speech
        :param language: Language of the input text
        :param path_audio_style: Path to audio file for style conditioning
        :return: BytesIO object containing the generated WAV audio
        """
        # Get conditioning latents for speaker style
        try:
            self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(
                audio_path=[path_audio_style]
            )
        except Exception as e:
            raise ValueError(f"Error obtaining conditioning latents: {e}")

        # Process text into chunks
        text_chunks = self.tts_process(text, language)

        # Generate audio chunks
        wav_chunks_total = []
        for sentences in text_chunks:
            
            try:
                wav_chunks = self.transcrition(sentences.strip(), language)
                wav_chunks_total.append(wav_chunks["wav"])
            except Exception as e:
                print(f"Error processing chunk: {e}")
                continue

        # Validate if any chunks were generated
        if not wav_chunks_total:
            raise ValueError("No audio chunks were generated")

        # Concatenate audio chunks
        try:
            combined_wav = torch.cat([
                torch.tensor(chunk) for chunk in wav_chunks_total
            ], dim=0)
        except Exception as e:
            raise ValueError(f"Error concatenating audio chunks: {e}")

        # Save to BytesIO
        try:
            wav_io = BytesIO()
            torchaudio.save(
                wav_io, 
                combined_wav.squeeze().unsqueeze(0).cpu(), 
                sample_rate=24000,  # Corrected sample rate
                format="wav"
            )
            wav_io.seek(0)
            return wav_io
        except Exception as e:
            raise ValueError(f"Error saving audio to BytesIO: {e}")
    
    
class KPipeline_TTS():
    def __init__(self,path_model,device,path_voices):
        path_config = os.path.join(path_model,'config.json')
        path_ckpt = os.path.join(path_model,'kokoro-v1_0.pth')
        with open(path_config,'r') as file_configs:
            self.config = json.load(file_configs)

        self.kmodel = KModel(
                                config=self.config,
                                model=path_ckpt
                                )
        self.path_voices = path_voices
        self.device = device
        self.lang_support = ['en', 'ja', 'zh', 'es', 'fr', 'hi', 'it', 'pt']
        self.spkears_manager = [id_spk.split('.')[0] for id_spk in os.listdir(path_voices)]
         
        
    def normarlize_language_code(self, language):
        language_dict = {
                        'en': 'a',
                        'ja': 'j',
                        'zh': 'z',
                        'es': 'e',
                        'fr': 'f',
                        'hi': 'h',
                        'it': 'i',
                        'pt': 'p'
                    }
        return language_dict[language]

    
    async def transcriable(self, text: str, language: str, id_speaker):
        
        language = self.normarlize_language_code(language=language)
        kpipeline_tts = KPipeline(
                            lang_code=language,
                            model=self.kmodel,
                            device=self.device,
                            )
        
        voice_tensor = torch.load(os.path.join(self.path_voices,(id_speaker + '.pt')))
        generator = kpipeline_tts(
                                    text,
                                    voice=voice_tensor,
                                    speed=1, 
                                    split_pattern=r'\n+'
                                )
        
        combined_audio = []  
        for i, (gs, ps, audio) in enumerate(generator):
            combined_audio.append(audio)
        
        # Concatenate the audio list into a single tensor
        if combined_audio:
            combined_audio_tensor = torch.cat(combined_audio, dim=-1)
            
            # Create BytesIO object
            wav_io = BytesIO()
            
            # Save the combined audio tensor
            torchaudio.save(wav_io, combined_audio_tensor.unsqueeze(0).cpu(), 22050, format="wav")
            wav_io.seek(0) 
            
            return wav_io

        # except Exception as e:
        #     raise ValueError(f'Error: {e}')
        

class Khmer_TTS():
    def __init__(self,path_model):
        self.model = VitsModel.from_pretrained(path_model)
        self.tokenizer = AutoTokenizer.from_pretrained(path_model)
        
    
    def khmer_sentence_split(self, text):

        sentence_endings = r"[។៕]"  
        sentences = re.split(rf"({sentence_endings})", text)

        result = []
        for i in range(0, len(sentences), 2):
            sentence = sentences[i].strip()
            if i + 1 < len(sentences):
                sentence += sentences[i + 1].strip()
            if sentence: 
                result.append(sentence)
        return result
    
    async def khmer_transcible(self, text):
        sentences = self.khmer_sentence_split(text=text)
        all_audio = []

        for sentence in sentences:
            start = time.time()
            inputs = self.tokenizer(sentence, return_tensors="pt")
            with torch.no_grad():
                # Generate the waveform from the model
                output = self.model(**inputs).waveform
            

            all_audio.append(output)


        concatenated_audio = torch.cat(all_audio, dim=-1)
        wav_io = BytesIO()
        
        if concatenated_audio.ndimension() == 3:

            concatenated_audio = concatenated_audio.squeeze(0)
        torchaudio.save(wav_io, concatenated_audio.cpu(), 16000, format="wav")
        # torchaudio.save(wav_io, concatenated_audio.unsqueeze(0).cpu(), 22050, format="wav")
        wav_io.seek(0) 
        
        return wav_io