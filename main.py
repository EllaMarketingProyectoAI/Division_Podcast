from flask import Flask, request, jsonify
from supabase_upload import procesar_video_y_subir

app = Flask(__name__)

# ✅ Ruta para el healthcheck
@app.route("/", methods=["GET"])
def health_check():
    return "✅ Service is running", 200

# Ruta principal POST
@app.route("/", methods=["POST"])
def dividir_podcast():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        url_video = data.get("url_video")
        supabase_file_name = data.get("supabaseFileName")

        if not user_id or not url_video or not supabase_file_name:
            return jsonify({"status": "error", "message": "Faltan campos requeridos"}), 400

        uploaded_urls = procesar_video_y_subir(user_id, url_video, supabase_file_name)
        return jsonify({"status": "success", "urls": uploaded_urls})

    except Exception as e:
        print(f"❌ Error general en Flask: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway usa esta variable automáticamente
    app.run(host="0.0.0.0", port=port)
