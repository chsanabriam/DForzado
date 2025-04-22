#!/bin/bash
# Importar red a Neo4j desde archivos CSV generados
# Uso: ./import_network.sh <ruta_nodos_csv> <ruta_relaciones_csv> <nombre_db>

# Validar parámetros
if [ "$#" -lt 2 ]; then
    echo "Uso: $0 <ruta_nodos_csv> <ruta_relaciones_csv> [nombre_db]"
    exit 1
fi

NODES_CSV=$1
RELS_CSV=$2
DB_NAME=${3:-neo4j}  # Por defecto 'neo4j' si no se especifica

# 1. Detener Neo4j pero mantener contenedor activo
echo "=== Deteniendo Neo4j ==="
docker compose exec neo4j neo4j stop

# 2. Copiar archivos CSV al contenedor
echo "=== Copiando archivos CSV al contenedor ==="
NEO4J_CONTAINER=$(docker compose ps -q neo4j)
docker cp "$NODES_CSV" "$NEO4J_CONTAINER:/var/lib/neo4j/import/nodes.csv"
docker cp "$RELS_CSV" "$NEO4J_CONTAINER:/var/lib/neo4j/import/relationships.csv"

# 3. Verificar que existen
echo "=== Verificando archivos en el contenedor ==="
docker compose exec neo4j ls -la /var/lib/neo4j/import/

# 4. Ejecutar importación
echo "=== Ejecutando neo4j-admin import ==="
docker compose exec neo4j neo4j-admin database import full \
    --nodes=/var/lib/neo4j/import/nodes.csv \
    --relationships=/var/lib/neo4j/import/relationships.csv \
    --delimiter=',' --id-type=STRING \
    --overwrite-destination \
    "$DB_NAME"

# 5. Iniciar Neo4j
echo "=== Iniciando Neo4j ==="
docker compose exec neo4j neo4j start

echo "=== Importación completada ==="