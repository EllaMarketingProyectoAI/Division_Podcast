import os
import uuid
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from ffmpeg_split import dividir_video
from os.path import basename, splitext

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(url, key)

def subir_a_supabase(file_path, bucket_path, mime_type):
    bucket_name = "videospodcast"

    with open(file_path, "rb") as f:
        data = f.read()

    supabase.storage.from_(bucket_name).upload(
        path=bucket_path,
        file=data,
        file_options={"content-type": mime_type},
        upsert=True
    )

    return f"{url}/storage/v1/object/public/{bucket_name}/{bucket_path}"
