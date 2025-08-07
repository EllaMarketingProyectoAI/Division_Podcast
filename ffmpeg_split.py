import os
import requests
import uuid
import subprocess
from supabase_upload import subir_a_supabase
import math
from moviepy.editor import VideoFileClip

def dividir_video(url_video, base_name, session_id):
    tmp_folder = "/tmp"
    local_filename = os.path.join(tmp_folder, f"{session_id}.mp4")

    # Descargar el archivo de Supabase al disco temporal
    subprocess.run(["curl", "-o", local_filename, url_video], check=True)

    # Obtener duración con MoviePy
    video = VideoFileClip(local_filename)
    duracion = math.floor(video.duration)
    video.close()

    partes = duracion // 600 + int(duracion % 600 > 0)
    resultados = []

    for i in range(partes):
        start = i * 600
        output_name = f"{base_name.replace('.mp4', '')}_clip{i+1}.mp4"
        output_mp4 = os.path.join(tmp_folder, output_name)
        output_mp3 = output_mp4.replace(".mp4", ".mp3")

        # Comprimir con crf 28 para archivos más ligeros
        comando_mp4 = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", local_filename,
            "-t", "600",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "28",
            "-c:a", "aac",
            output_mp4
        ]
        subprocess.run(comando_mp4, check=True)

        comando_mp3 = [
            "ffmpeg", "-y",
            "-i", output_mp4,
            "-q:a", "0",
            "-map", "a",
            output_mp3
        ]
        subprocess.run(comando_mp3, check=True)

        resultados.append({
            "n": i + 1,
            "nombre": output_name,
            "ruta_mp4": output_mp4,
            "ruta_mp3": output_mp3
        })

    # Eliminar el video original descargado
    os.remove(local_filename)

    return resultados

