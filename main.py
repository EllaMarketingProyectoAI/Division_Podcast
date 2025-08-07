from flask import Flask, request, jsonify
from supabase_upload import subir_archivos
from ffmpeg_split import dividir_video_en_segmentos
import os
import uuid
import requests
import logging
from dotenv import load_dotenv
from supabase import create_client

# Logging para debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return "✅ Service is running", 200

@app.route("/", methods=["POST"])
def dividir_y_subir():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        video_url = data.get("url_video")
        base_filename = data.get("supabaseFileName")

        if not user_id or not video_url or not base_filename:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # 1. Descargar video
        temp_video_path = f"/tmp/{uuid.uuid4()}_{base_filename}"
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(temp_video_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # 2. Dividir
        output_dir = f"/tmp/clips_{uuid.uuid4()}"
        os.makedirs(output_dir, exist_ok=True)
        clips = dividir_video_en_segmentos(temp_video_path, output_dir, base_filename)

        # 3. Subir
        urls = subir_archivos(clips, base_filename)

        # 4. Limpiar
        os.remove(temp_video_path)
        for mp4, mp3 in clips:
            os.remove(mp4)
            os.remove(mp3)
        os.rmdir(output_dir)

        return jsonify({"status": "success", "clips": urls})
        
    except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    print("🔥 Error completo:", error_details)
    return jsonify({"status": "error", "message": str(e), "details": error_details}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)


