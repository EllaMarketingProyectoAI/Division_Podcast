from flask import Flask, request, jsonify
import os
import uuid
from ffmpeg_split import dividir_video_en_segmentos
from supabase_upload import upload_clip_to_supabase

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return {"status": "ok", "message": "Servidor funcionando en Railway ✅"}

@app.route("/")
def health():
    return "OK", 200

@app.route("/", methods=["POST"])
def dividir_podcast():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        url_video = data.get("url_video")
        supabase_file_name = data.get("supabaseFileName")

        if not user_id or not url_video or not supabase_file_name:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # Descargar el video temporalmente
        local_video_path = f"/tmp/{supabase_file_name}"
        os.system(f"wget '{url_video}' -O {local_video_path}")

        # Crear carpeta temporal para los clips
        clips_dir = f"/tmp/clips_{uuid.uuid4()}"
        os.makedirs(clips_dir, exist_ok=True)

        # Dividir video
        clips = dividir_video_en_segmentos(local_video_path, clips_dir)

        # Subir a Supabase
        urls = []
        for clip in clips:
            upload_clip_to_supabase(clip, user_id, supabase_file_name)
            urls.append(clip)

        return jsonify({
            "status": "success",
            "message": f"{len(urls)} clips created and uploaded",
            "clips": urls
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
