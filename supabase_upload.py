
import os
import uuid
import requests
from supabase import create_client
from dotenv import load_dotenv
from ffmpeg_split import dividir_video_en_segmentos

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def procesar_video_y_subir(user_id, url_video, supabase_file_name):
    local_video_path = f"/tmp/{supabase_file_name}"

    try:
        response = requests.get(url_video, stream=True)
        response.raise_for_status()
        with open(local_video_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al descargar el video: {e}")
        return ["Error al descargar el video"]

    clips_dir = f"/tmp/clips_{uuid.uuid4()}"
    os.makedirs(clips_dir, exist_ok=True)

    try:
        clips = dividir_video_en_segmentos(local_video_path, clips_dir)
    except Exception as e:
        print(f"❌ Error al dividir el video: {e}")
        return ["Error al dividir el video"]

    uploaded_urls = []

    for clip_path in clips:
        try:
            file_name = os.path.basename(clip_path)
            storage_path = f"{user_id}/{file_name}"

            with open(clip_path, "rb") as file_data:
                supabase.storage.from_(BUCKET_NAME).upload(storage_path, file_data, {"content-type": "video/mp4"})

            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
            uploaded_urls.append(public_url)
        except Exception as e:
            print(f"❌ Error al subir clip {clip_path}: {e}")

    return uploaded_urls

