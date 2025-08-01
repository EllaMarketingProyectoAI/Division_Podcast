import os
import subprocess

def dividir_video_en_segmentos(input_path, output_dir, duracion_segmento=600):
    output_paths = []

    comando_duracion = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_path
    ]
    resultado = subprocess.run(comando_duracion, capture_output=True, text=True)
    duracion_total = float(resultado.stdout.strip())

    inicio = 0
    index = 1

    while inicio < duracion_total:
        salida_clip = os.path.join(output_dir, f"temp_clip_{index}.mp4")
        comando = [
            "ffmpeg", "-ss", str(inicio), "-i", input_path,
            "-t", str(duracion_segmento), "-c", "copy", salida_clip, "-y"
        ]
        subprocess.run(comando, check=True)
        output_paths.append(salida_clip)
        inicio += duracion_segmento
        index += 1

    return output_paths
