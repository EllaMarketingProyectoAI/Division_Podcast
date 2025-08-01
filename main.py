
from flask import Flask, request, jsonify
import os
from supabase_upload import procesar_video_y_subir

app = Flask(__name__)

@app.route("/", methods=["GET"])
def healthcheck():
    return jsonify({"message": "Servidor funcionando en Railway ✅", "status": "ok"})

@app.route("/", methods=["POST"])
def procesar_post():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        url_video = data.get("url_video")
        supabase_file_name = data.get("supabaseFileName")

        print(f"👤 User ID: {user_id}")
        print(f"🎥 URL: {url_video}")
        print(f"🗂️ Archivo: {supabase_file_name}")

        uploaded_urls = procesar_video_y_subir(user_id, url_video, supabase_file_name)
        return jsonify({"status": "ok", "urls": uploaded_urls})

    except Exception as e:
        print(f"❌ Error general en POST: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
