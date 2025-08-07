import os
import subprocess

def dividir_video_en_segmentos(input_path, output_dir, base_output_name, duracion_segmento=600):
    output_paths = []

    # 1. Obtener duración total
    comando_duracion = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_path
    ]
    resultado = subprocess.run(comando_duracion, capture_output=True, text=True)
    duracion_total = float(resultado.stdout.strip())

    inicio = 0
    index = 1

    while inicio < duracion_total:
        mp4_output = os.path.join(output_dir, f"{base_output_name}_clip{index}.mp4")
        mp3_output = os.path.join(output_dir, f"{base_output_name}_clip{index}.mp3")

        # 2. Crear clip de video
        comando_mp4 = [
            "ffmpeg", "-ss", str(inicio), "-i", input_path,
            "-t", str(duracion_segmento),
            "-c:v", "libx264", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "128k",
            mp4_output, "-y"
        ]
        subprocess.run(comando_mp4, check=True)

        # 3. Extraer audio
        comando_mp3 = [
            "ffmpeg", "-i", mp4_output,
            "-vn", "-acodec", "libmp3lame", "-q:a", "2",
            mp3_output, "-y"
        ]
        subprocess.run(comando_mp3, check=True)

        output_paths.append((mp4_output, mp3_output))
        inicio += duracion_segmento
        index += 1

    return output_paths
