# 1. Imagen base
FROM python:3.12-slim

# 2. Establecer directorio de trabajo
WORKDIR /app

# 3. Instalar dependencias del sistema (como ffmpeg y wget)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar archivos del proyecto
COPY . .

# 6. Exponer puerto (opcional, pero recomendado)
EXPOSE 8000

# 7. Comando de arranque
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:3000"]
