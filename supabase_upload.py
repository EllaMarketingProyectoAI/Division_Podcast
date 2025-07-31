import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = "videospodcast"

def upload_clip_to_supabase(filepath, user_id, video_id):
    filename = os.path.basename(filepath)
    storage_path = f"ClipsPodcast/{user_id}/{video_id}/{filename}"

    with open(filepath, "rb") as f:
        supabase.storage.from_(BUCKET_NAME).upload(storage_path, f)

    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
    print(f"✅ Subido: {storage_path} → {public_url}")
    return public_url
