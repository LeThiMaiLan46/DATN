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
from src.sevices.tts_services import TTS_Vi_Services
from dotenv import load_dotenv
# from pydub import AudioSegment
import torchaudio
import tempfile
import shutil
load_dotenv()

router = APIRouter()

#====== define config path ============
tts_path_model = os.environ.get('VI_TTS_PATH_MODEL')
tts_configs = os.environ.get('VI_TTS_CONFIGS')

path_audio_style = os.environ.get('AUDIO_SAMPLE_DIR')


tts_sevices = TTS_Vi_Services(
                            path_model=tts_path_model,
                            path_config=tts_configs
                        )

#====== list API to use ============
@router.post("/api/v1/text/phonemize")
async def tts_transcribable(
    text: str = Form(...),
    language: str = Form(...),
    audio_id: str = Form(None),
    audio: UploadFile = File(None),
    audio_type: str = Form(...),
    sample_name: str = Form(None)
):
    path_audio_style = None

    if audio:
        upload_dir = "uploads/audio_inputs"
        os.makedirs(upload_dir, exist_ok=True)

        audio_path = os.path.join(upload_dir, "audio.wav")

        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        path_audio_style = audio_path

    # Gọi xử lý TTS, giả sử trả về BytesIO chứa file wav
    response = await tts_sevices.tts_transcribable(
        text=text,
        language=language,
        path_audio_style=path_audio_style
    )

    # Đọc dữ liệu âm thanh từ BytesIO bằng torchaudio
    waveform, sample_rate = torchaudio.load(io.BytesIO(response.getvalue()))

    # Resample về 22050 nếu cần
    target_sample_rate = 22050
    if sample_rate != target_sample_rate:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sample_rate)
        waveform = resampler(waveform)

    # Lưu file tạm với sample rate 22050
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        torchaudio.save(temp_file.name, waveform, sample_rate=target_sample_rate)
        temp_file_path = temp_file.name

    return FileResponse(temp_file_path, media_type="audio/wav", filename="audio.wav")
    
    
    # text = request.text
    # language = request.language
    # audio_id = request.audio_id


    # response = await tts_sevices.tts_transcribable(
    #                             text=text,
    #                             language=language,
    #                             path_audio_style=path_audio_style
    #                             )
    # with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
    #     temp_file.write(response.getvalue())
    #     temp_file_path = temp_file.name
    #     # Return the WAV file as a FileResponse (equivalent to Flask's send_file)
    #     return FileResponse(temp_file_path, media_type="audio/wav", filename="audio.wav")

