import os
import uuid
import requests
from dotenv import load_dotenv
from supabase import create_client
from ffmpeg_split import dividir_video_en_segmentos

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def procesar_video_y_subir(user_id, url_video, supabase_file_name):
    local_video_path = f"/tmp/{supabase_file_name}"
    
    # Descargar video
    try:
        response = requests.get(url_video, stream=True)
        response.raise_for_status()
        with open(local_video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"❌ Error al descargar video: {e}")
        return []

    # Crear carpeta temporal para clips
    clips_dir = f"/tmp/clips_{uuid.uuid4()}"
    os.makedirs(clips_dir, exist_ok=True)

    # Cortar el video en segmentos
    clips = dividir_video_en_segmentos(local_video_path, clips_dir)

    uploaded_urls = []

    for index, clip_path in enumerate(clips, start=1):
        filename = f"{supabase_file_name}_clip{index}.mp4"
        storage_path = f"PodcastCortados/{filename}"

        try:
            with open(clip_path, "rb") as f:
                supabase.storage.from_(BUCKET_NAME).upload(
                    storage_path, f, {"content-type": "video/mp4"}
                )
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
            uploaded_urls.append(public_url)
        except Exception as e:
            print(f"❌ Error al subir {filename}: {e}")

    return uploaded_urls
