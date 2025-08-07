import os
import uuid
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from ffmpeg_split import dividir_video
from os.path import basename, splitext



SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file_to_supabase(file_path, supabase_path, content_type=None):
    bucket = "videospodcast"
    
    # Detectar MIME si no se especifica
    if not content_type:
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        data = f.read()

    supabase.storage.from_(bucket).upload(
        path=supabase_path,
        file=data,
        file_options={
            "content-type": content_type,
            "x-upsert": "true"
        }
    )

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{supabase_path}"
    return public_url
