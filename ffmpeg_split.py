import os
import requests
import uuid
import subprocess
from supabase_upload import subir_a_supabase
import math
from moviepy.video.io.VideoFileClip import VideoFileClip
import time
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operación cancelada por timeout")

def descargar_con_progreso(url_video, local_filename, timeout=300):
    """
    Descarga el archivo con timeout y progreso
    """
    try:
        print(f"Descargando video desde: {url_video}")
        start_time = time.time()
        
        # Usar requests con streaming para archivos grandes
        response = requests.get(url_video, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Mostrar progreso cada 10MB
                    if downloaded % (10 * 1024 * 1024) == 0:
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"Descargado: {progress:.1f}% ({downloaded / (1024*1024):.1f}MB)")
                        
                    # Verificar timeout
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Timeout en descarga")
        
        download_time = time.time() - start_time
        print(f"Descarga completada en {download_time:.2f} segundos")
        return True
        
    except Exception as e:
        print(f"Error en descarga: {str(e)}")
        if os.path.exists(local_filename):
            os.remove(local_filename)
        raise

def ejecutar_ffmpeg_con_timeout(comando, timeout=600):
    """
    Ejecuta comando ffmpeg con timeout
    """
    try:
        print(f"Ejecutando: {' '.join(comando)}")
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
                
            execution_time = time.time() - start_time
            print(f"FFmpeg completado en {execution_time:.2f} segundos")
            return True
            
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise TimeoutError(f"FFmpeg timeout después de {timeout} segundos")
            
    except Exception as e:
        print(f"Error en FFmpeg: {str(e)}")
        raise

def dividir_video(url_video, base_name, session_id):
    tmp_folder = "/tmp"
    local_filename = os.path.join(tmp_folder, f"{session_id}.mp4")
    
    try:
        # Descargar con timeout y progreso
        descargar_con_progreso(url_video, local_filename, timeout=600)  # 10 minutos max
        
        # Verificar que el archivo se descargó correctamente
        if not os.path.exists(local_filename):
            raise Exception("El archivo no se descargó correctamente")
            
        file_size = os.path.getsize(local_filename)
        print(f"Archivo descargado: {file_size / (1024*1024):.2f} MB")
        
        # Obtener duración con timeout
        print("Analizando duración del video...")
        video = None
        try:
            video = VideoFileClip(local_filename)
            duracion = math.floor(video.duration)
            print(f"Duración del video: {duracion} segundos ({duracion/60:.1f} minutos)")
        finally:
            if video:
                video.close()
        
        # Calcular partes (clips de 10 minutos = 600 segundos)
        partes = duracion // 600 + int(duracion % 600 > 0)
        print(f"Se crearán {partes} clips de máximo 10 minutos cada uno")
        
        resultados = []
        
        for i in range(partes):
            start = i * 600
            clip_duration = min(600, duracion - start)  # Duración real del clip
            
            output_name = f"{base_name.replace('.mp4', '')}_clip{i+1}.mp4"
            output_mp4 = os.path.join(tmp_folder, output_name)
            output_mp3 = output_mp4.replace(".mp4", ".mp3")
            
            print(f"\nProcesando clip {i+1}/{partes} (inicio: {start}s, duración: {clip_duration}s)")
            
            # Comando optimizado para archivos grandes
            comando_mp4 = [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-i", local_filename,  # Siempre usar el archivo original descargado
                "-t", str(clip_duration),
                "-c:v", "libx264",
                "-preset", "ultrafast",  # Más rápido para archivos grandes
                "-crf", "28",
                "-c:a", "aac",
                "-avoid_negative_ts", "make_zero",  # Evitar problemas de timestamp
                "-fflags", "+genpts",  # Generar timestamps
                output_mp4
            ]
            
            # Ejecutar con timeout de 15 minutos por clip
            ejecutar_ffmpeg_con_timeout(comando_mp4, timeout=900)
            
            # Verificar que el clip se creó
            if not os.path.exists(output_mp4):
                raise Exception(f"No se pudo crear el clip {i+1}")
                
            clip_size = os.path.getsize(output_mp4)
            print(f"Clip MP4 creado: {clip_size / (1024*1024):.2f} MB")
            
            # Extraer audio con timeout
            comando_mp3 = [
                "ffmpeg", "-y",
                "-i", output_mp4,
                "-q:a", "2",  # Calidad media para reducir tamaño
                "-map", "a",
                output_mp3
            ]
            
            ejecutar_ffmpeg_con_timeout(comando_mp3, timeout=300)  # 5 minutos para audio
            
            # Verificar que el audio se creó
            if not os.path.exists(output_mp3):
                raise Exception(f"No se pudo crear el audio del clip {i+1}")
                
            audio_size = os.path.getsize(output_mp3)
            print(f"Audio MP3 creado: {audio_size / (1024*1024):.2f} MB")
            
            resultados.append({
                "n": i + 1,
                "nombre": output_name,
                "ruta_mp4": output_mp4,
                "ruta_mp3": output_mp3,
                "duracion": clip_duration,
                "tamaño_mb4": round(clip_size / (1024*1024), 2),
                "tamaño_mp3": round(audio_size / (1024*1024), 2)
            })
        
        print(f"\n✅ Procesamiento completado: {len(resultados)} clips creados")
        return resultados
        
    except Exception as e:
        print(f"❌ Error en dividir_video: {str(e)}")
        raise
        
    finally:
        # Limpiar archivo original
        if os.path.exists(local_filename):
            try:
                os.remove(local_filename)
                print("Archivo original eliminado")
            except:
                print("No se pudo eliminar el archivo original")

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
            print(f"Error limpiando {clip['nombre']}: {str(e)}")
    
    print("Archivos temporales limpiados")
