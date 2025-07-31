from flask import Flask, request, jsonify
import os, tempfile, uuid
from moviepy.editor import VideoFileClip
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "videospodcast")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def subir_y_dividir():
    try:
        print("✅ POST recibido")
        if 'video' not in request.files:
            return jsonify({"status": "error", "message": "No se recibió archivo 'video'"}), 400

        video_file = request.files['video']
        print(f"📥 Nombre recibido: {video_file.filename}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            video_file.save(tmp.name)
            temp_video_path = tmp.name

        print("🎬 Abriendo video con MoviePy...")
        video = VideoFileClip(temp_video_path)
        duration = video.duration
        segment_duration = 600
        output_dir = tempfile.mkdtemp()
        urls_clips = []

        for i, start in enumerate(range(0, int(duration), segment_duration)):
            end = min(start + segment_duration, duration)
            clip = video.subclip(start, end)
            output_filename = f"{uuid.uuid4()}_clip_{i+1}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            print(f"✂️ Clip {i+1}: {start}-{end}")

            clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                threads=1,
                preset="ultrafast"
            )

            # Subir a Supabase
            with open(output_path, "rb") as f:
                supabase.storage.from_(BUCKET_NAME).upload(
                    f"clips/temp/{output_filename}",
                    f,
                    {"content-type": "video/mp4"},
                    upsert=True
                )

            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/clips/temp/{output_filename}"
            urls_clips.append(public_url)

        return jsonify({"status": "success", "clips": urls_clips}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500
