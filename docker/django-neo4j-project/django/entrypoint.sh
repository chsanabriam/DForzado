#!/bin/bash

# Esperar a que Neo4j esté disponible
echo "Esperando a que Neo4j esté disponible..."
while ! nc -z neo4j 7687; do
  sleep 1
done
echo "Neo4j está disponible"

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones
python manage.py migrate

# Iniciar Gunicorn
gunicorn myproject.wsgi:application --bind 0.0.0.0:8000