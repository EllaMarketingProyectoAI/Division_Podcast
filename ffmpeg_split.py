import os
import uuid
import subprocess

def dividir_video_en_segmentos(input_path, output_dir, base_output_name, duracion_segmento=600):
    output_paths = []

    try:
        # Obtener duración del video
        comando_duracion = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", input_path
        ]
        resultado = subprocess.run(comando_duracion, capture_output=True, text=True, check=True)
        duracion_total = float(resultado.stdout.strip())

        # Limpiar doble extensión .mp4 si existe
        if base_output_name.endswith(".mp4"):
            base_output_name = base_output_name[:-4]

        inicio = 0
        index = 1

        while inicio < duracion_total:
            salida_clip = os.path.join(output_dir, f"{base_output_name}_clip{index}.mp4")
            tiempo_duracion = min(duracion_segmento, duracion_total - inicio)

            comando = [
                "ffmpeg", "-v", "error",
                "-ss", str(inicio), "-i", input_path,
                "-t", str(tiempo_duracion),
                "-c:v", "libx264", "-preset", "veryfast", "-threads", "1", "-bufsize", "512k",
                "-c:a", "aac", "-b:a", "96k",
                salida_clip, "-y"
            ]

            subprocess.run(comando, check=True)
            output_paths.append(salida_clip)

            inicio += duracion_segmento
            index += 1

        return output_paths

    except subprocess.CalledProcessError as e:
        print("❌ Error en FFmpeg:", e)
        raise e
    except Exception as e:
        print("❌ Error general:", e)
        raise e
