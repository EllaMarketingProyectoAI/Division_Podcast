import os
import uuid
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from ffmpeg_split import dividir_video_en_segmentos
from os.path import basename, splitext

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "videospodcast"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def subir_archivos(lista_archivos, nombre_base):
    urls = []

    # Quitar extensión del nombre base
    nombre_limpio = os.path.splitext(nombre_base)[0]

    for i, (mp4_path, mp3_path) in enumerate(lista_archivos, start=1):
        mp4_dest = f"PodcastCortados/{nombre_limpio}_clip{i}.mp4"
        mp3_dest = f"PodcastCortadosAudio/{nombre_limpio}_clip{i}.mp3"

        with open(mp4_path, "rb") as f:
            supabase.storage.from_(BUCKET_NAME).upload(mp4_dest, f, {"x-upsert": "true"})

        with open(mp3_path, "rb") as f:
            supabase.storage.from_(BUCKET_NAME).upload(mp3_dest, f, {"x-upsert": "true"})

        urls.append({
            "clip": i,
            "video_url": f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{mp4_dest}",
            "audio_url": f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{mp3_dest}"
        })

    return urls
