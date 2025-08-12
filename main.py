from flask import Flask, request, jsonify
from supabase_upload import subir_a_supabase
from ffmpeg_split import dividir_video
import os
import uuid
import requests
from dotenv import load_dotenv
from supabase import create_client
import pkg_resources
print("INSTALLED PACKAGES:", [p.key for p in pkg_resources.working_set])

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return "✅ Service is running", 200

@app.route('/', methods=['POST'])
def dividir_podcast():
    try:
        data = request.get_json()
        user_id = data['user_id']
        url_video = data['url_video']
        supabase_file_name = data['supabaseFileName']

        # Generar ID de sesión
        session_id = str(uuid.uuid4())

        # Ejecutar función de división
        clips_info = dividir_video(url_video, supabase_file_name, session_id)

        # Subir todos los clips a Supabase
        resultados = []
        for clip in clips_info:
            url_video_supabase = subir_a_supabase(
                clip['ruta_mp4'], 
                f"PodcastCortados/{clip['nombre']}", 
                "video/mp4"
            )
            url_audio_supabase = subir_a_supabase(
                clip['ruta_mp3'], 
                f"PodcastCortadosAudio/{clip['nombre'].replace('.mp4', '.mp3')}", 
                "audio/mpeg"
            )
            resultados.append({
                "clip": clip['n'],
                "video_url": url_video_supabase,
                "audio_url": url_audio_supabase
            })

        return jsonify({"status": "success", "clips": resultados})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port = "5000")
