import subprocess
import os
import imageio_ffmpeg

# Verifica si ffmpeg está disponible
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
print(f"🔧 FFMPEG path: {ffmpeg_path}")

def dividir_video_en_segmentos(video_path, output_dir, duracion_segmento=600):
    nombre_base = os.path.splitext(os.path.basename(video_path))[0]

    output_pattern = os.path.join(output_dir, f"{nombre_base}_%03d.mp4")

    comando = [
        "ffmpeg",
        "-i", video_path,
        "-c", "copy",
        "-map", "0",
        "-segment_time", str(duracion_segmento),
        "-f", "segment",
        "-reset_timestamps", "1",
        output_pattern
    ]

    subprocess.run(comando, check=True)

    # Lista de rutas generadas
    return [
        os.path.join(output_dir, f)
        for f in sorted(os.listdir(output_dir))
        if f.startswith(nombre_base) and f.endswith(".mp4")
    ]
