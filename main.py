from flask import Flask, jsonify
import os
from supabase_upload import subir_a_supabase

app = Flask(__name__)

@app.route("/")
def healthcheck():
    return jsonify({"message": "Servidor funcionando en Railway ✅", "status": "ok"})

@app.route("/procesar")
def procesar():
    subir_a_supabase()
    return jsonify({"message": "Procesamiento iniciado ✅", "status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
