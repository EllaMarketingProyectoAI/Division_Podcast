import os
import math
import requests
import subprocess
import uuid
from moviepy.editor import VideoFileClip
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "videospodcast"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def sanitize_filename(filename):
    if filename.endswith(".mp4"):
        return filename[:-4]
    return filename

def download_video(video_url, local_filename):
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(1024 * 1024):
                f.write(chunk)
    else:
        raise Exception(f"Error al descargar el video: {response.status_code}")

def get_video_duration(path):
    clip = VideoFileClip(path)
    duration = int(clip.duration)
    clip.close()
    return duration

def split_and_upload(video_path, output_base_name, user_id):
    duration = get_video_duration(video_path)
    segment_duration = 600  # 10 min
    num_clips = math.ceil(duration / segment_duration)
    uploaded_urls = []

    for i in range(num_clips):
        start = i * segment_duration
        output_filename = f"{output_base_name}_clip{i + 1}.mp4"
        output_path = os.path.join("/tmp", output_filename)

        command = [
            "ffmpeg", "-ss", str(start), "-i", video_path,
            "-t", str(segment_duration),
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-b:a", "128k",
            "-y", output_path
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al generar el clip {i + 1}: {e}")
            continue

        with open(output_path, "rb") as f:
            storage_path = f"PodcastCortados/{output_filename}"
            supabase.storage.from_(BUCKET_NAME).upload(storage_path, f, {"x-upsert": "true"})

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{storage_path}"
        uploaded_urls.append(public_url)

        os.remove(output_path)

    return uploaded_urls
