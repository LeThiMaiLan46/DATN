from typing import List
from pydantic import BaseModel


class TTS_Request(BaseModel):
    text:str = "Hi, good morning!"
    language:str = "en"
    audio_id:str = "en_sample"
    
class Delete_audio(BaseModel):
    audio_id:str = "audio_id"
    language:str = "en"