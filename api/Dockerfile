# 1) Imagen base ligera con Python 3.13 (la misma versión con la que se guardó el pipeline)
FROM python:3.13-slim

# 2) Ajustes de Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3) Paquetes del sistema: curl, para el healthcheck de Docker Compose
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# 4) Directorio de trabajo dentro del contenedor
WORKDIR /app

# 5) Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copiar el código de la aplicación y el modelo
COPY . .

# 7) Crear y usar un usuario no-root (buena práctica de seguridad)
RUN useradd -u 1000 -m appuser && chown -R appuser:appuser /app
USER appuser

# 8) Documentar el puerto interno
EXPOSE 8000

# 9) Comando por defecto: lanzar Uvicorn en 0.0.0.0:8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
