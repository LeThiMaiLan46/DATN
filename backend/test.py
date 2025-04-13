# import os
# import time
# import torch
# import torchaudio
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts

# print("Loading model...")
# config = XttsConfig()
# config.load_json("/app/tts_services/models_vi/config.json")
# model = Xtts.init_from_config(config)
# model.load_checkpoint(config, checkpoint_dir="/app/tts_services/models_vi/", use_deepspeed=True)
# model.cuda()

# print("Computing speaker latents...")
# gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["/app/tts_services/audio_storage/en/en_sample5.wav"])

# print("Inference...")
# t0 = time.time()
# chunks = model.inference_stream(
#     "xin chào buổi sáng, hôm nay bạn iu có nhiều việc không?",
#     "vi",
#     gpt_cond_latent,
#     speaker_embedding
# )

# wav_chuncks = []
# print('======== chunks : ',chunks)
# for i, chunk in enumerate(chunks):
#     if i == 0:
#         print(f"Time to first chunck: {time.time() - t0}")
#     print(f"Received chunk {i} of audio length {chunk.shape[-1]}")
#     wav_chuncks.append(chunk)
# wav = torch.cat(wav_chuncks, dim=0)
# torchaudio.save("xtts_streaming.wav", wav.squeeze().unsqueeze(0).cpu(), 24000)







import os
import torch
import torchaudio
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

print("Loading model...")
config = XttsConfig()
config.load_json("/app/tts_services/models/config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="/app/tts_services/models/", use_deepspeed=True)
model.cuda()

print("Computing speaker latents...")
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["/app/tts_services/audio_storage/vi/vi_sample3.wav"])

print("Inference...")
out = model.inference(
    "xin chào buổi sáng bạnnnn iuu, hôm nay bạn đi làm nhiều việc không",
    "vi",
    gpt_cond_latent,
    speaker_embedding,
    temperature=0.3,
    length_penalty=1.0,
    repetition_penalty=10.0,
    top_k=30,
    top_p=0.85,
    enable_text_splitting=True
)
torchaudio.save("xtts.wav", torch.tensor(out["wav"]).unsqueeze(0), 24000)