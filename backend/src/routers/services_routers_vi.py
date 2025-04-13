import os
import io
import logging
import requests
import tempfile
import torch
import uuid
from fastapi import APIRouter, Depends, Request
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, Response
from fastapi.responses import StreamingResponse
from src.models.payload import TTS_Request, Delete_audio
from src.sevices.text2speech import TTS_Vi_Services
from src.utils.minio_worker import Minio_Worker
from dotenv import load_dotenv


load_dotenv()

router = APIRouter()

#====== define config path ============
tts_path_model = os.environ.get('VI_TTS_PATH_MODEL')
tts_configs = os.environ.get('VI_TTS_CONFIGS')
path_audio_stogare = os.environ.get('PATH_AUDIO_STOGARE')

minio_access_key = os.environ.get('MINIO_ACCESS_KEY')
minio_secret_key = os.environ.get('MINIO_SECRET_KEY')
minio_hostname = os.environ.get('MINIO_HOSTNAME')
minio_bucket_name= os.environ.get('MINIO_BUKET_NAME')

#====== __init__ services ============
minio_workers = Minio_Worker(
                                minio_hostname=minio_hostname,
                                access_key=minio_access_key,
                                secret_key=minio_secret_key,
                                bucket_name=minio_bucket_name
                            )

tts_sevices = TTS_Vi_Services(
                            path_model=tts_path_model,
                            path_config=tts_configs
                        )



#====== list API to use ============
@router.post("/api/v1/text/phonemize")
async def tts_transcribable(request:TTS_Request):
    text = request.text
    language = request.language
    audio_id = request.audio_id
    audio_style = minio_workers.get_file_from_minio_server(
                                                            path_audio_stogare= path_audio_stogare,
                                                            original_name=audio_id,
                                                            language = language
                                                            )
    if audio_style['status'] == 200:
        path_audio_style = audio_style['audio_dir']
        response = await tts_sevices.tts_transcribable(
                                    text=text,
                                    language=language,
                                    path_audio_style=path_audio_style
                                    )
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(response.getvalue())
            temp_file_path = temp_file.name
            # Return the WAV file as a FileResponse (equivalent to Flask's send_file)
            return FileResponse(temp_file_path, media_type="audio/wav", filename="audio.wav")
    else:
        return audio_style

