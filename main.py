from flask import Flask, request, jsonify
import os
import uuid
from ffmpeg_split import dividir_video_en_segmentos
from supabase_upload import subir_a_supabase

app = Flask(__name__)

@app.route("/", methods=["POST"])
def dividir_podcast():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        url_video = data.get("url_video")
        supabase_file_name = data.get("supabaseFileName")

        if not user_id or not url_video or not supabase_file_name:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        # 1. Descargar el video
        local_filename = f"/tmp/{uuid.uuid4()}.mp4"
        os.system(f"wget '{url_video}' -O {local_filename}")

        # 2. Dividir el video
        output_dir = f"/tmp/{uuid.uuid4()}"
        os.makedirs(output_dir, exist_ok=True)
        partes = dividir_video_en_segmentos(local_filename, output_dir)

        # 3. Subir a Supabase
        urls = []
        for parte in partes:
            url = subir_a_supabase(parte, user_id)
            urls.append(url)

        return jsonify({
            "status": "success",
            "clips_uploaded": len(urls),
            "clip_urls": urls
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
