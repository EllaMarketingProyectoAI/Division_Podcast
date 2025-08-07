import os
import requests
import uuid
import subprocess
from supabase_upload import upload_file_to_supabase

def dividir_video(url_video, supabase_file_name, user_id, tmp_folder):
    temp_video_path = os.path.join(tmp_folder, "original_video.mp4")

    # Descargar video
    response = requests.get(url_video, stream=True)
    with open(temp_video_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Obtener duración total
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", temp_video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    duracion_total = float(result.stdout)
    duracion_clip = 600  # 10 minutos
    cantidad_clips = int(duracion_total // duracion_clip) + 1

    base_name = os.path.splitext(supabase_file_name)[0]

    urls_clips = []

    for i in range(cantidad_clips):
        start_time = i * duracion_clip
        clip_name = f"{base_name}_clip{i+1}"

        video_clip_path = os.path.join(tmp_folder, f"{clip_name}.mp4")
        audio_clip_path = os.path.join(tmp_folder, f"{clip_name}.mp3")

        # Cortar video y asegurar compatibilidad
        comando_video = [
            "ffmpeg", "-y", "-i", temp_video_path,
            "-ss", str(start_time), "-t", str(duracion_clip),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
            "-c:a", "aac",
            video_clip_path
        ]
        subprocess.run(comando_video, check=True)

        # Extraer audio
        comando_audio = [
            "ffmpeg", "-y", "-i", video_clip_path,
            "-q:a", "0", "-map", "a", audio_clip_path
        ]
        subprocess.run(comando_audio, check=True)

        # Subir a Supabase
        url_video = upload_file_to_supabase(video_clip_path, f"PodcastCortados/{clip_name}.mp4", "video/mp4")
        url_audio = upload_file_to_supabase(audio_clip_path, f"PodcastCortadosAudio/{clip_name}.mp3", "audio/mpeg")

        urls_clips.append({
            "clip": i + 1,
            "video_url": url_video,
            "audio_url": url_audio
        })

    # Limpiar temporal
    os.remove(temp_video_path)
    for file in os.listdir(tmp_folder):
        os.remove(os.path.join(tmp_folder, file))
    os.rmdir(tmp_folder)

    return urls_clips
