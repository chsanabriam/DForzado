FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear y establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crea el proyecto de Django (si no está ya creado)
# RUN django-admin startproject myproject .

# Copiar código del proyecto
COPY . .

# Asegurar que el script de entrada sea ejecutable
RUN chmod +x entrypoint.sh

# Puerto en el que correrá Gunicorn
EXPOSE 8000

# Ejecutar el script de entrada
ENTRYPOINT ["sh", "/app/entrypoint.sh"]