# django/dashboard/management/commands/cargar_redn4j_masiva_csv.py

import os
import subprocess
import tempfile
import time
import csv
import requests
import shutil
import networkx as nx
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from myproject.neo4j_driver import Neo4jConnection
from dashboard.utils_neo4j import crear_red_desde_consolidado, calcular_metricas_centralidad

class Command(BaseCommand):
    help = 'Importa una red a Neo4j usando neo4j-admin import, usando el mismo flujo que crear_red_neo4j'

    def add_arguments(self, parser):
        parser.add_argument('archivo_consolidado', type=str, help='Ruta al archivo CSV consolidado')
        parser.add_argument('--delimiter', type=str, default=',', help='Delimitador CSV')
        parser.add_argument('--id-type', type=str, default='STRING', help='Tipo de ID (STRING, INTEGER, etc.)')
        parser.add_argument('--output-dir', type=str, default=None, help='Directorio donde guardar los CSV generados')
        parser.add_argument('--database', type=str, default='neo4j', help='Nombre de la base de datos Neo4j')
        parser.add_argument('--sin-metricas', action='store_true', help='No calcular métricas de centralidad (más rápido para redes grandes)',)
    
    def handle(self, *args, **options):
        # Cerrar la conexión a Neo4j si existe
        self.stdout.write(self.style.WARNING('Cerrando conexiones a Neo4j...'))
        Neo4jConnection.close()
        
        archivo_consolidado = options.get('archivo_consolidado')
        output_dir = options.get('output_dir')
        database = options.get('database')
        calcular_metricas = not options.get('sin_metricas')
        
        # Verificar que el archivo existe
        if not os.path.exists(archivo_consolidado):
            raise CommandError(f'Archivo CSV consolidado no encontrado: {archivo_consolidado}')
        
        if calcular_metricas:
            self.stdout.write(self.style.SUCCESS('Se calcularán métricas de centralidad'))
        else:
            self.stdout.write(self.style.SUCCESS('No se calcularán métricas de centralidad'))
        
        # 1. Crear la red desde el consolidado usando la función existente
        self.stdout.write(self.style.WARNING(f'Creando red desde {archivo_consolidado}...'))
        try:
            G = crear_red_desde_consolidado(archivo_consolidado)
            self.stdout.write(self.style.SUCCESS(
                f'Red creada con {G.number_of_nodes()} nodos y {G.number_of_edges()} relaciones'
            ))
            # Guardar la red para uso futuro
            import pickle
            with open('red_consolidado.pickle', 'wb') as f:
                pickle.dump(G, f)
            self.stdout.write(self.style.SUCCESS('Red guardada en archivo red_consolidado.pickle'))
        except Exception as e:
            raise CommandError(f'Error al crear red desde consolidado: {e}')
        
        # Calcular métricas si se solicita
        if calcular_metricas:
            tiempo_metricas_inicio = time.time()
            self.stdout.write(self.style.SUCCESS('Calculando métricas de centralidad...'))
            try:
                # Calcular métricas solo para una muestra si la red es muy grande
                if len(G) > 100000:
                    self.stdout.write(self.style.WARNING(
                        f'Red muy grande ({len(G)} nodos), calculando métricas parciales'
                    ))
                    import random
                    # Tomar una muestra de 50000 nodos o el 10% de la red, lo que sea mayor
                    sample_size = max(50000, int(len(G) * 0.1))
                    sample_nodes = random.sample(list(G.nodes()), sample_size)
                    G_sample = G.subgraph(sample_nodes)
                    metricas = calcular_metricas_centralidad(G_sample)
                else:
                    metricas = calcular_metricas_centralidad(G)
                
                tiempo_metricas = time.time() - tiempo_metricas_inicio
                self.stdout.write(self.style.SUCCESS(f'Métricas calculadas en {tiempo_metricas:.2f} segundos'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al calcular métricas: {str(e)}'))
                self.stdout.write(self.style.WARNING('Continuando sin métricas...'))
        
        
        # 2. Generar los archivos CSV para neo4j-admin import
        nodes_file, rels_file = self._network_to_csv(G, output_dir)
        self.stdout.write(self.style.SUCCESS(f'CSVs generados: {nodes_file} y {rels_file}'))
        
        # 3. Proporcionar instrucciones para importar
        self.stdout.write(self.style.WARNING(
            'IMPORTANTE: Para completar la importación, ejecuta los siguientes comandos desde tu host (no desde Django):'
        ))
        
        # Generar instrucciones para el usuario
        self.stdout.write("\n# 1. Detén el servicio Neo4j pero mantén el contenedor activo")
        self.stdout.write("docker-compose exec neo4j neo4j stop")
        
        self.stdout.write("\n# 2. Copia los archivos CSV al contenedor")
        self.stdout.write(f"docker cp {nodes_file} $(docker-compose ps -q neo4j):/var/lib/neo4j/import/nodes.csv")
        self.stdout.write(f"docker cp {rels_file} $(docker-compose ps -q neo4j):/var/lib/neo4j/import/relationships.csv")
        
        self.stdout.write("\n# 3. Verifica que los archivos existen en el contenedor")
        self.stdout.write("docker-compose exec neo4j ls -la /var/lib/neo4j/import/")
        
        self.stdout.write("\n# 4. Ejecuta neo4j-admin database import")
        cmd = (
            "docker-compose exec neo4j neo4j-admin database import full "
            "--nodes=/var/lib/neo4j/import/nodes.csv "
            "--relationships=/var/lib/neo4j/import/relationships.csv "
            f"--delimiter='{options['delimiter']}' "
            f"--id-type={options['id_type']} "
            "--overwrite-destination "
            f"{database}"
        )
        self.stdout.write(cmd)
        
        self.stdout.write("\n# 5. Inicia Neo4j nuevamente")
        self.stdout.write("docker-compose exec neo4j neo4j start")
        
        self.stdout.write(self.style.SUCCESS('\nArchivos CSV generados correctamente.'))
    
    def _network_to_csv(self, G, output_dir=None):
        """Convierte una red NetworkX a CSVs para neo4j-admin import"""
        # Crear directorio temporal
        # Crear directorio para los archivos CSV
        if output_dir:
            csv_dir = output_dir
            os.makedirs(csv_dir, exist_ok=True)
        else:
            csv_dir = tempfile.mkdtemp()
        
        nodes_file = os.path.join(csv_dir, 'nodes.csv')
        rels_file = os.path.join(csv_dir, 'relationships.csv')

        
        # Escribir nodos a CSV
        self.stdout.write('Exportando nodos a CSV...')
        with open(nodes_file, 'w', newline='') as f:
            # Obtener todas las propiedades de los nodos
            all_props = set()
            for _, attrs in G.nodes(data=True):
                all_props.update(attrs.keys())
            
            # Crear encabezados
            headers = ['id:ID'] + list(all_props) + [':LABEL']
            writer = csv.writer(f)
            writer.writerow(headers)
            
            # Escribir datos de nodos
            count = 0
            for node_id, attrs in G.nodes(data=True):
                row = [node_id]
                for prop in all_props:
                    # Convertir valores a string y manejar None
                    val = attrs.get(prop, '')
                    row.append(str(val) if val is not None else '')
                
                # Determinar el tipo de nodo (Persona o NUNC) basado en sus atributos o ID
                if 'tipo' in attrs and attrs['tipo'] == 'nunc':
                    node_label = 'NUNC'
                elif 'tipo' in attrs and attrs['tipo'] == 'persona':
                    node_label = 'Persona'
                else:
                    # Lógica para detectar si es un NUNC o Persona basado en el patrón del ID
                    if node_id.isdigit() or (node_id.startswith('N') and node_id[1:].isdigit()):
                        node_label = 'NUNC'
                    else:
                        node_label = 'Persona'
                
                row.append(node_label)
                writer.writerow(row)
                
                count += 1
                if count % 10000 == 0:
                    self.stdout.write(f'  Procesados {count} nodos')
        
        # Escribir relaciones a CSV
        self.stdout.write('Exportando relaciones a CSV...')
        with open(rels_file, 'w', newline='') as f:
            # Obtener todas las propiedades de las relaciones
            all_props = set()
            for _, _, attrs in G.edges(data=True):
                all_props.update(attrs.keys())
            
            # Crear encabezados
            headers = [':START_ID', ':END_ID'] + list(all_props) + [':TYPE']
            writer = csv.writer(f)
            writer.writerow(headers)
            
            # Escribir datos de relaciones
            count = 0
            for source, target, attrs in G.edges(data=True):
                # Determinar el tipo de relación desde los atributos
                rel_type = attrs.get('tipo', 'RELACIONADO')
                
                row = [source, target]
                for prop in all_props:
                    # Convertir valores a string y manejar None
                    val = attrs.get(prop, '')
                    row.append(str(val) if val is not None else '')
                row.append(rel_type)
                writer.writerow(row)
                
                count += 1
                if count % 10000 == 0:
                    self.stdout.write(f'  Procesadas {count} relaciones')
        
        return nodes_file, rels_file