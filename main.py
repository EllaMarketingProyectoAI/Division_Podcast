from flask import Flask, request, jsonify
from supabase_upload import procesar_video_y_subir
from ffmpeg_split import dividir_video_en_segmentos
import os
import uuid
import requests
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return "✅ Service is running", 200

@app.route("/", methods=["POST"])
def dividir_podcast():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        url_video = data.get("url_video")
        supabase_file_name = data.get("supabaseFileName")

        if not user_id or not url_video or not supabase_file_name:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        temp_dir = f"/tmp/clips_{uuid.uuid4()}"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = f"/tmp/{supabase_file_name}"
        response = requests.get(url_video)
        with open(temp_path, "wb") as f:
            f.write(response.content)

        base_name = os.path.splitext(supabase_file_name)[0]
        output_paths = dividir_video_en_segmentos(temp_path, temp_dir, base_name)

        public_urls = []
        for clip_path in output_paths:
            file_name = os.path.basename(clip_path)
            with open(clip_path, "rb") as f:
                supabase.storage.from_(BUCKET_NAME).upload(
                    f"PodcastCortados/{file_name}", f, {"x-upsert": "true"}
                )
            url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/PodcastCortados/{file_name}"
            public_urls.append(url)

        return jsonify({"status": "success", "clips": public_urls}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
