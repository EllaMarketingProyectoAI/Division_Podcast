import os
import uuid
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
    os.system(f"wget '{url_video}' -O {local_video_path}")

    clips_dir = f"/tmp/clips_{uuid.uuid4()}"
    os.makedirs(clips_dir, exist_ok=True)

    clips = dividir_video_en_segmentos(local_video_path, clips_dir)

    uploaded_urls = []

    for clip_path in clips:
        file_name = os.path.basename(clip_path)
        storage_path = f"{user_id}/{file_name}"

        with open(clip_path, "rb") as file_data:
            supabase.storage.from_(BUCKET_NAME).upload(storage_path, file_data, {"content-type": "video/mp4"})

        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        uploaded_urls.append(public_url)

    return uploaded_urls
