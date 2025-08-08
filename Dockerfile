ponlo en el codigo lel cambio
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
RUN python -c "import moviepy; print('moviepy:', moviepy.__file__); import os; print(os.listdir(os.path.dirname(moviepy.__file__)))"

RUN pip install --upgrade pip setuptools wheel

COPY . .

RUN python -c "import ssl; print(ssl.OPENSSL_VERSION)"

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall --no-cache-dir imageio imageio-ffmpeg scipy numpy decorator tqdm
RUN pip uninstall -y moviepy && pip install --no-cache-dir --force-reinstall moviepy

EXPOSE 5000

CMD ["python", "-c", "import pkg_resources; print('INSTALLED:', [p.key for p in pkg_resources.working_set]); import moviepy.editor"]
