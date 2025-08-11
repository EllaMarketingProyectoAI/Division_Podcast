import os
import requests
import uuid
import subprocess
from supabase_upload import subir_a_supabase
import json
import math
from moviepy.video.io.VideoFileClip import VideoFileClip
import time
import signal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operación cancelada por timeout")

def descargar_con_progreso(url_video, local_filename, timeout=300):
    """
    Descarga el archivo con timeout y progreso
    """
    try:
        logger.info(f"Descargando video desde: {url_video}")
        start_time = time.time()

        response = requests.get(url_video, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if downloaded % (10 * 1024 * 1024) == 0:
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"Descargado: {progress:.1f}% ({downloaded / (1024*1024):.1f}MB)")

                    if time.time() - start_time > timeout:
                        raise TimeoutError("Timeout en descarga")

        download_time = time.time() - start_time
        logger.info(f"Descarga completada en {download_time:.2f} segundos")
        return True

    except Exception as e:
        logger.error(f"Error en descarga: {str(e)}")
        if os.path.exists(local_filename):
            os.remove(local_filename)
        raise

def ejecutar_ffmpeg_con_timeout(comando, timeout=600):
    """
    Ejecuta comando ffmpeg con timeout
    """
    try:
        start_time = time.time()

        process = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, comando, stderr)

            return True

        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise TimeoutError(f"FFmpeg timeout después de {timeout} segundos")

    except Exception as e:
        raise

def obtener_duracion_video_ffprobe(ruta_video):
    comando = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", ruta_video
    ]
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(resultado.stdout.strip())

def obtener_duracion_audio_ffprobe(ruta_video):
    comando = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", ruta_video
    ]
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(resultado.stdout.strip())

def dividir_video(url_video, base_name, session_id):
    tmp_folder = "/tmp"
    local_filename = os.path.join(tmp_folder, f"{session_id}.mp4")

    logger.info("DEBUG: Entrando a dividir_video")
    try:
        descargar_con_progreso(url_video, local_filename, timeout=600)  # 10 minutos max

        if not os.path.exists(local_filename):
            raise Exception("El archivo no se descargó correctamente")

        file_size = os.path.getsize(local_filename)

        try:
            duracion_video = obtener_duracion_video_ffprobe(local_filename)
            duracion_audio = obtener_duracion_audio_ffprobe(local_filename)
            duracion = min(duracion_video, duracion_audio)
            logger.info(f"DEBUG: duracion={duracion}, partes={math.ceil(duracion / 600)}")
            if not duracion or duracion <= 0:
                raise ValueError("No se pudo obtener la duración válida del video/audio.")
        except Exception as e:
            raise ValueError(f"Error al obtener la duración del video/audio: {e}")

        partes = math.ceil(duracion / 600)
        resultados = []
        for i in range(partes):
            start = i * 600
            clip_duration = min(600, duracion - start)
            logger.info(f"DEBUG: i={i}, start={start}, clip_duration={clip_duration}, duracion={duracion}")
            if start >= duracion:
                continue
            if clip_duration <= 0:
                continue

            output_name = f"{base_name.replace('.mp4', '')}_clip{i+1}.mp4"
            output_mp4 = os.path.join(tmp_folder, output_name)
            output_mp3 = output_mp4.replace(".mp4", ".mp3")

            comando_mp4 = [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-i", local_filename,
                "-t", str(clip_duration),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "28",
                "-c:a", "aac",
                output_mp4
            ]

            try:
                logger.info(f"DEBUG: Ejecutando ffmpeg para clip {i+1}")
                ejecutar_ffmpeg_con_timeout(comando_mp4, timeout=900)

                if i + 1 == partes:
                    logger.info(f"DEBUG: Último clip, output_mp4: {output_mp4}, existe: {os.path.exists(output_mp4)}, tamaño: {os.path.getsize(output_mp4) if os.path.exists(output_mp4) else 'N/A'}")

                if not os.path.exists(output_mp4):
                    raise Exception(f"No se pudo crear el clip {i+1}")

                clip_size = os.path.getsize(output_mp4)

                comando_mp3 = [
                    "ffmpeg", "-y",
                    "-i", output_mp4,
                    "-q:a", "2",
                    "-map", "a",
                    output_mp3
                ]

                logger.info(f"DEBUG: Ejecutando ffmpeg para audio clip {i+1}")
                ejecutar_ffmpeg_con_timeout(comando_mp3, timeout=300)

                if i + 1 == partes:
                    logger.info(f"DEBUG: Último clip, output_mp3: {output_mp3}, existe: {os.path.exists(output_mp3)}, tamaño: {os.path.getsize(output_mp3) if os.path.exists(output_mp3) else 'N/A'}")

                if not os.path.exists(output_mp3):
                    raise Exception(f"No se pudo crear el audio del clip {i+1}")

                audio_size = os.path.getsize(output_mp3)

                resultados.append({
                    "n": i + 1,
                    "nombre": output_name,
                    "ruta_mp4": output_mp4,
                    "ruta_mp3": output_mp3,
                    "duracion": clip_duration,
                    "tamaño_mb4": round(clip_size / (1024*1024), 2),
                    "tamaño_mp3": round(audio_size / (1024*1024), 2),
                    "error": None
                })
            except Exception as e:
                if i + 1 == partes:
                    logger.info(f"DEBUG: Error procesando el último clip: {str(e)}")
                resultados.append({
                    "n": i + 1,
                    "nombre": output_name,
                    "ruta_mp4": None,
                    "ruta_mp3": None,
                    "duracion": clip_duration,
                    "tamaño_mb4": 0,
                    "tamaño_mp3": 0,
                    "error": str(e)
                })
        return resultados
    except Exception as e:
        raise
    finally:
        if os.path.exists(local_filename):
            try:
                os.remove(local_filename)
            except:
                pass

def limpiar_archivos_temporales(clips_info):
    """
    Limpia los archivos temporales después de subirlos
    """
    for clip in clips_info:
        try:
            if os.path.exists(clip['ruta_mp4']):
                os.remove(clip['ruta_mp4'])
            if os.path.exists(clip['ruta_mp3']):
                os.remove(clip['ruta_mp3'])
        except Exception as e:
            logger.error(f"Error limpiando {clip['nombre']}: {str(e)}")

    logger.info("Archivos temporales limpiados")
