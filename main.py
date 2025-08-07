from flask import Flask, request, jsonify
from ffmpeg_split import dividir_video
import os

app = Flask(__name__)

@app.route("/", methods=["POST"])
def procesar_video():
    try:
        data = request.get_json()
        user_id = data["user_id"]
        url_video = data["url_video"]
        supabase_file_name = data["supabaseFileName"]

        # Crear carpeta temporal por usuario para evitar conflictos
        tmp_folder = f"/tmp/{user_id}"
        os.makedirs(tmp_folder, exist_ok=True)

        resultado = dividir_video(url_video, supabase_file_name, user_id, tmp_folder)

        return jsonify({"status": "success", "clips": resultado})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
