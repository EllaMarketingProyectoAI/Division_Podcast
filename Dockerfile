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

# CMD de debug temporal: imprime paquetes e intenta importar moviepy.editor
CMD ["python", "-c", "import pkg_resources; print('INSTALLED:', [p.key for p in pkg_resources.working_set]); import moviepy.editor"]
