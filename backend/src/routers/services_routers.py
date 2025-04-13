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
from src.sevices.text2speech import TTS_Services, KPipeline_TTS, Khmer_TTS
from src.sevices.image_generator import Text_to_Images
from src.utils.minio_worker import Minio_Worker
from dotenv import load_dotenv


load_dotenv()

router = APIRouter()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
#====== define config path ============
tts_path_model = os.environ.get('TTS_PATH_MODEL')
tts_configs = os.environ.get('TTS_CONFIGS')
path_audio_stogare = os.environ.get('PATH_AUDIO_STOGARE')

minio_access_key = os.environ.get('MINIO_ACCESS_KEY')
minio_secret_key = os.environ.get('MINIO_SECRET_KEY')
minio_hostname = os.environ.get('MINIO_HOSTNAME')
minio_bucket_name= os.environ.get('MINIO_BUKET_NAME')

text_to_images_path_model = os.environ.get('TEXT2IMAGES_PATH_MODEL')
#====== __init__ services ============
minio_workers = Minio_Worker(
                                minio_hostname=minio_hostname,
                                access_key=minio_access_key,
                                secret_key=minio_secret_key,
                                bucket_name=minio_bucket_name
                            )

tts_sevices = TTS_Services(
                            path_model=tts_path_model,
                            path_config=tts_configs
                        )


text2images_service = Text_to_Images(text_to_images_path_model)

kpipeline_tts = KPipeline_TTS(
                            path_model=os.environ.get('KOKORO_PATH_MODEL'),
                            device=device,
                            path_voices=os.environ.get('PATH_VOICES')
                            )

khmer_tts = Khmer_TTS(os.environ.get('PATH_KHMER_MODEL'))

#====== list API to use ============
@router.post("/api/v1/text/phonemize")
async def tts_transcribable(request:TTS_Request):
    text = request.text
    language = request.language
    audio_id = request.audio_id
    path_audio_style=''
    
    #============== using kokoro TTS model ==============================
    if language in kpipeline_tts.lang_support and audio_id in kpipeline_tts.spkears_manager:
        response = await kpipeline_tts.transcriable(
                                        text=text,
                                        language=language,
                                        id_speaker=audio_id
                                        )
    elif language =='km':
        response = await khmer_tts.khmer_transcible(text)
        
    else: #========== using coqui TTS model ==================
        audio_style = minio_workers.get_file_from_minio_server(
                                                                path_audio_stogare= path_audio_stogare,
                                                                original_name=audio_id,
                                                                language = language
                                                                )
        if audio_style['status'] == 200:
            path_audio_style = audio_style['audio_dir']
        else:
            return audio_style
    
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


@router.post("/api/v1/text/delete_audio")
def delete_audio_Minio(request:Delete_audio):
    audio_id = request.audio_id
    path_language_folder = os.path.join(path_audio_stogare,request.language)
    audio_name = audio_id.strip() + '.wav'
    path_filename = os.path.join(path_language_folder,audio_name)
    
    # path_audio = os.path.join(path_audio_stogare,audio_name)
    if os.path.exists(path_filename):
        os.remove(path_filename)
        return {
            "status":200,
            "messagges": f"Deleted audio id : {audio_id}"
        }
    else:
        return {
            "status":400,
            "messagges": f"Audio id : {audio_id} not found!"
        }



@router.post("/api/v1/image/generator")
def generate_images(
    prompt: str = Form(...),
    seed: int = Form(None),
    guidance: float = Form(5.0),
):
    try:
        # Generate images using your existing function
        images = text2images_service.generate_image(prompt, seed, guidance)
        
        # Since your function returns a list of PIL Images, handle single or multiple images
        if not images:
            raise HTTPException(status_code=404, detail="No images were generated")

        # Convert the first image to bytes
        img_byte_arr = io.BytesIO()
        images[0].save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        # Return the image with proper headers
        return Response(
            content=img_byte_arr.getvalue(),
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="generated_{uuid.uuid4()}.png"'
            }
        )

    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise HTTPException(
            status_code=500,
            detail="GPU memory exhausted. Please try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )