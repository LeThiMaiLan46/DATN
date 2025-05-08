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
from src.utils.text_input_normalize import expand_abbreviations


from src.utils.text_split import split_by_char_limit_multilingual

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
        text_abbreviations = expand_abbreviations(new_text)
        return text_abbreviations
    
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
    
