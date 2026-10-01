# Imagen base de Python
FROM python:3.12-slim

# Variables de entorno: salida de Python sin buffer y sin .pyc
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar primero las dependencias para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# El proyecto usa base de datos relacional (SQLite local o MySQL vía .env).
# EXPOSE indica el puerto interno donde Django escuchará.
EXPOSE 8000

# Comando por defecto: servidor de desarrollo de Django.
# En producción se recomienda Gunicorn + Nginx (ver docs/DESPLIEGUE_EC2.md).
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
