import os
import math
import subprocess
from moviepy.editor import VideoFileClip

def dividir_video(input_path, output_dir, base_filename, segmento_duracion=600):
    try:
        video = VideoFileClip(input_path)
        duracion_total = video.duration
        video.close()
    except Exception as e:
        print(f"[❌] Error al cargar el video: {e}")
        return []

    total_segmentos = math.ceil(duracion_total / segmento_duracion)
    urls = []

    for i in range(total_segmentos):
        inicio = i * segmento_duracion
        duracion_clip = min(segmento_duracion, duracion_total - inicio)

        # Evita generar clips menores a 1 segundo (podrían estar corruptos)
        if duracion_clip < 1:
            print(f"[⚠️] Clip {i + 1} ignorado por ser muy corto ({duracion_clip}s)")
            continue

        output_filename = f"{base_filename}_clip{i+1}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        comando = [
            "ffmpeg", "-ss", str(inicio), "-i", input_path,
            "-t", str(duracion_clip),
            "-vf", "scale=1280:720",              # ⚠️ Baja resolución
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-b:a", "128k",
            output_path, "-y"
        ]

        try:
            subprocess.run(comando, check=True)
            print(f"[✅] Clip generado: {output_filename}")
            urls.append(output_path)
        except subprocess.CalledProcessError as e:
            print(f"[❌] Error generando el clip {i + 1}: {e}")
            continue

    return urls
