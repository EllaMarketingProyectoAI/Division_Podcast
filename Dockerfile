# Fuerza Rebuild
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && pip install moviepy && pip freeze

EXPOSE 5000

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000"]
