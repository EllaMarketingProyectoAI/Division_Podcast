import os
import math
import tempfile
import subprocess
from supabase import create_client
from moviepy.editor import VideoFileClip
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "videospodcast"
FOLDER_NAME = "PodcastCortados"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def clean_filename(name):
    if name.endswith(".mp4"):
        return name[:-4]
    return name

def dividir_video(video_url, supabase_filename):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            local_video_path = os.path.join(tmpdir, "input.mp4")
            # Descargar el video desde Supabase
            video_response = supabase.storage.from_(BUCKET_NAME).download(video_url.split("/object/public/")[1])
            with open(local_video_path, "wb") as f:
                f.write(video_response)

            # Calcular duración
            video = VideoFileClip(local_video_path)
            duration = math.ceil(video.duration)  # segundos
            clip_duration = 600  # 10 minutos
            num_clips = math.ceil(duration / clip_duration)
            video.close()

            base_filename = clean_filename(supabase_filename)

            urls = []

            for i in range(num_clips):
                start = i * clip_duration
                output_path = os.path.join(tmpdir, f"{base_filename}_clip{i+1}.mp4")

                command = [
                    "ffmpeg",
                    "-ss", str(start),
                    "-t", str(clip_duration),
                    "-i", local_video_path,
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "28",
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-y",
                    output_path
                ]

                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg error: {result.stderr.decode()}")

                # Subir a Supabase
                with open(output_path, "rb") as f:
                    data = f.read()

                upload_path = f"{FOLDER_NAME}/{base_filename}_clip{i+1}.mp4"

                supabase.storage.from_(BUCKET_NAME).upload(
                    path=upload_path,
                    file=data,
                    file_options={"content-type": "video/mp4"},
                    options={"x-upsert": "true"}
                )

                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{upload_path}"
                urls.append(public_url)

            return {"status": "success", "urls": urls}

    except Exception as e:
        return {"status": "error", "message": str(e)}
