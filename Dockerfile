FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && apt-get clean

RUN pip install --upgrade pip setuptools

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall --no-cache-dir imageio imageio-ffmpeg scipy numpy decorator tqdm
RUN pip uninstall -y moviepy && pip install --no-binary=:all: --force-reinstall moviepy

EXPOSE 5000

CMD ["python", "-c", "import pkg_resources; print('INSTALLED:', [p.key for p in pkg_resources.working_set]); import moviepy.editor"]
