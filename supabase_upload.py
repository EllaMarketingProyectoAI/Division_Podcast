import os
import uuid
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
import time

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(url, key)

def subir_a_supabase_streaming(file_path, bucket_path, mime_type, chunk_size=8192):
    """
    Sube archivos a Supabase usando streaming para evitar cargar todo en memoria
    """
    bucket_name = "videospodcast"
    
    if not file_path or not os.path.exists(file_path):
        print(f"Archivo no encontrado o ruta inválida: {file_path}")
        return None
    
    try:
        # Obtener el tamaño del archivo
        file_size = os.path.getsize(file_path)
        print(f"Subiendo archivo: {file_path} ({file_size / (1024*1024):.2f} MB)")
        
        # Para archivos muy grandes, usar chunks
        if file_size > 50 * 1024 * 1024:  # Si es mayor a 50MB
            return subir_archivo_grande(file_path, bucket_path, mime_type)
        
        # Para archivos medianos, subir de una vez pero con timeout
        with open(file_path, "rb") as f:
            start_time = time.time()
            
            supabase.storage.from_(bucket_name).upload(
                path=bucket_path,
                file=f,  # Pasar el file object directamente
                file_options={"content-type": mime_type}
                # upsert eliminado
            )
            
            upload_time = time.time() - start_time
            print(f"Archivo subido en {upload_time:.2f} segundos")
            
        return f"{url}/storage/v1/object/public/{bucket_name}/{bucket_path}"
        
    except Exception as e:
        print(f"Error subiendo {file_path}: {str(e)}")
        # Intentar una vez más con método alternativo
        return subir_con_requests(file_path, bucket_path, mime_type)

def subir_archivo_grande(file_path, bucket_path, mime_type):
    """
    Para archivos muy grandes, usar requests directamente con streaming
    """
    bucket_name = "videospodcast"
    
    upload_url = f"{url}/storage/v1/object/{bucket_name}/{bucket_path}"
    
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': mime_type,
        'x-upsert': 'true'  # Puedes quitar este header si da error
    }
    
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                upload_url,
                headers=headers,
                data=f,
                timeout=300
            )
            
        if response.status_code in [200, 201]:
            return f"{url}/storage/v1/object/public/{bucket_name}/{bucket_path}"
        else:
            raise Exception(f"Error HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error en subida de archivo grande: {str(e)}")
        raise

def subir_con_requests(file_path, bucket_path, mime_type):
    """
    Método alternativo usando requests directamente
    """
    bucket_name = "videospodcast"
    upload_url = f"{url}/storage/v1/object/{bucket_name}/{bucket_path}"
    
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': mime_type,
        'x-upsert': 'true'  # Puedes quitar este header si da error
    }
    
    with open(file_path, 'rb') as f:
        response = requests.post(
            upload_url,
            headers=headers,
            data=f,
            timeout=180
        )
    
    if response.status_code in [200, 201]:
        return f"{url}/storage/v1/object/public/{bucket_name}/{bucket_path}"
    else:
        raise Exception(f"Error en subida alternativa: {response.status_code}")

def subir_a_supabase(file_path, bucket_path, mime_type):
    return subir_a_supabase_streaming(file_path, bucket_path, mime_type)
