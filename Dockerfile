FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && apt-get clean

RUN pip install --upgrade pip setuptools

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall --no-cache-dir moviepy imageio imageio-ffmpeg scipy numpy decorator tqdm

EXPOSE 5000

CMD ["python", "-c", "import pkg_resources; print('INSTALLED:', [p.key for p in pkg_resources.working_set]); import moviepy.editor"]
