from flask import Flask, jsonify
import os
from supabase_upload import procesar_video_y_subir

app = Flask(__name__)

@app.route("/")
def healthcheck():
    return jsonify({"message": "Servidor funcionando en Railway ✅", "status": "ok"})

@app.route("/procesar", methods=["GET"])
def procesar():
    try:
        clips = procesar_video_y_subir()
        return jsonify({"status": "success", "clips": clips})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
