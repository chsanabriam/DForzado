# django/dashboard/management/commands/cargar_redn4j_masiva_csv.py

import os
import subprocess
import tempfile
import time
import csv
import json
import requests
import shutil
import networkx as nx
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from myproject.neo4j_driver import Neo4jConnection
from dashboard.utils_neo4j import crear_red_desde_consolidado, calcular_metricas_centralidad, crear_red_desde_json

class Command(BaseCommand):
    help = 'Importa una red a Neo4j usando neo4j-admin import, usando el mismo flujo que crear_red_neo4j'

    def add_arguments(self, parser):
        parser.add_argument('archivo_consolidado', type=str, help='Ruta al archivo CSV consolidado')
        parser.add_argument('--delimiter', type=str, default=',', help='Delimitador CSV')
        parser.add_argument('--id-type', type=str, default='STRING', help='Tipo de ID (STRING, INTEGER, etc.)')
        parser.add_argument('--output-dir', type=str, default=None, help='Directorio donde guardar los CSV generados')
        parser.add_argument('--database', type=str, default='neo4j', help='Nombre de la base de datos Neo4j')
        parser.add_argument('--sin-metricas', action='store_true', help='No calcular métricas de centralidad (más rápido para redes grandes)')
        parser.add_argument('--archivo-nodos-json', type=str, default=None, help='Ruta al archivo JSON con nodos de entidades')
        parser.add_argument('--archivo-enlaces-json', type=str, default=None, help='Ruta al archivo JSON con enlaces de entidades')
        parser.add_argument('--solo-entidades', action='store_true', help='Cargar solamente la red de entidades (no CSV)')
    
    def handle(self, *args, **options):
        # Cerrar la conexión a Neo4j si existe
        self.stdout.write(self.style.WARNING('Cerrando conexiones a Neo4j...'))
        Neo4jConnection.close()
        
        archivo_consolidado = options.get('archivo_consolidado')
        output_dir = options.get('output_dir')
        database = options.get('database')
        calcular_metricas = not options.get('sin_metricas')
        archivo_nodos_json = options.get('archivo_nodos_json')
        archivo_enlaces_json = options.get('archivo_enlaces_json')
        solo_entidades = options.get('solo_entidades')
        
        # Variable para almacenar el grafo
        G = None
        
        # Verificar parámetros según el modo
        if solo_entidades:
            if not archivo_nodos_json or not archivo_enlaces_json:
                raise CommandError('En modo solo-entidades, se requieren --archivo-nodos-json y --archivo-enlaces-json')
        else:
            # Verificar que el archivo CSV existe
            if not os.path.exists(archivo_consolidado):
                raise CommandError(f'Archivo CSV consolidado no encontrado: {archivo_consolidado}')
        
        if calcular_metricas:
            self.stdout.write(self.style.SUCCESS('Se calcularán métricas de centralidad'))
        else:
            self.stdout.write(self.style.SUCCESS('No se calcularán métricas de centralidad'))
        
        # 1. Si hay archivos JSON de entidades, primero crear la red con estas entidades
        if archivo_nodos_json and archivo_enlaces_json:
            # Verificar que los archivos existen
            if not os.path.exists(archivo_nodos_json):
                raise CommandError(f'Archivo JSON de nodos no encontrado: {archivo_nodos_json}')
            if not os.path.exists(archivo_enlaces_json):
                raise CommandError(f'Archivo JSON de enlaces no encontrado: {archivo_enlaces_json}')
                
            self.stdout.write(self.style.WARNING(f'Cargando nodos desde {archivo_nodos_json}...'))
            self.stdout.write(self.style.WARNING(f'Cargando enlaces desde {archivo_enlaces_json}...'))
            
            try:
                # Cargar los archivos JSON
                with open(archivo_nodos_json, 'r', encoding='utf-8') as f:
                    nodos_json = json.load(f)
                    self.stdout.write(f"Cargados {len(nodos_json)} nodos desde JSON")
                    
                    # Verificación del formato
                    if nodos_json and isinstance(nodos_json, list) and 'id' in nodos_json[0]:
                        self.stdout.write(self.style.SUCCESS("Formato de nodos JSON válido"))
                    else:
                        self.stdout.write(self.style.ERROR("Formato de nodos JSON no reconocido"))
                
                with open(archivo_enlaces_json, 'r', encoding='utf-8') as f:
                    enlaces_json = json.load(f)
                    self.stdout.write(f"Cargados {len(enlaces_json)} enlaces desde JSON")
                    
                    # Verificación del formato
                    if enlaces_json and isinstance(enlaces_json, list) and 'source' in enlaces_json[0] and 'target' in enlaces_json[0]:
                        self.stdout.write(self.style.SUCCESS("Formato de enlaces JSON válido"))
                    else:
                        self.stdout.write(self.style.ERROR("Formato de enlaces JSON no reconocido"))
                
                # Crear la red desde los datos JSON
                G = crear_red_desde_json(nodos_json, enlaces_json)
                self.stdout.write(self.style.SUCCESS(
                    f'Red de entidades creada con {G.number_of_nodes()} nodos y {G.number_of_edges()} relaciones'
                ))
                
                # Si es solo entidades, no continuamos con el CSV
                if solo_entidades:
                    # Guardar la red para uso futuro
                    import pickle
                    with open('red_entidades.pickle', 'wb') as f:
                        pickle.dump(G, f)
                    self.stdout.write(self.style.SUCCESS('Red guardada en archivo red_entidades.pickle'))
                    
                    # Continuar directamente con la exportación a CSV y las instrucciones
                    nodes_file, rels_file = self._network_to_csv(G, output_dir)
                    self.stdout.write(self.style.SUCCESS(f'CSVs generados: {nodes_file} y {rels_file}'))
                    
                    # Mostrar instrucciones y terminar
                    self._show_import_instructions(nodes_file, rels_file, options)
                    return
            except Exception as e:
                raise CommandError(f'Error al crear red desde archivos JSON: {e}')
        
        # 2. Crear la red desde el consolidado usando la función existente (solo si no es modo solo-entidades)
        if not solo_entidades:
            self.stdout.write(self.style.WARNING(f'Creando red desde {archivo_consolidado}...'))
            try:
                # Si ya tenemos una red de entidades, la pasamos como parámetro
                if G:
                    self.stdout.write(self.style.WARNING('Integrando red de entidades con datos del CSV...'))
                    
                # Pasar el grafo G como argumento a crear_red_desde_consolidado
                G = crear_red_desde_consolidado(archivo_consolidado, grafo_existente=G)
                self.stdout.write(self.style.SUCCESS(
                    f'Red combinada con {G.number_of_nodes()} nodos y {G.number_of_edges()} relaciones'
                ))
                
                # Guardar la red para uso futuro
                import pickle
                with open('red_consolidado.pickle', 'wb') as f:
                    pickle.dump(G, f)
                self.stdout.write(self.style.SUCCESS('Red guardada en archivo red_consolidado.pickle'))
            except Exception as e:
                raise CommandError(f'Error al crear red desde consolidado: {e}')
        
        # Calcular métricas si se solicita
        if calcular_metricas and G:
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
        
        # 3. Generar los archivos CSV para neo4j-admin import
        if G:
            nodes_file, rels_file = self._network_to_csv(G, output_dir)
            self.stdout.write(self.style.SUCCESS(f'CSVs generados: {nodes_file} y {rels_file}'))
            
            # 4. Proporcionar instrucciones para importar
            self._show_import_instructions(nodes_file, rels_file, options)
        else:
            self.stdout.write(self.style.ERROR('No se ha creado ninguna red. Verifica los parámetros.'))
    
    def _show_import_instructions(self, nodes_file, rels_file, options):
        """Muestra las instrucciones para importar los CSVs a Neo4j"""
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
            f"{options['database']}"
        )
        self.stdout.write(cmd)
        
        self.stdout.write("\n# 5. Inicia Neo4j nuevamente")
        self.stdout.write("docker-compose exec neo4j neo4j start")
        
        self.stdout.write(self.style.SUCCESS('\nArchivos CSV generados correctamente.'))
    
    def _network_to_csv(self, G, output_dir=None):
        """Convierte una red NetworkX a CSVs para neo4j-admin import"""
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
        with open(nodes_file, 'w', newline='', encoding='utf-8') as f:
            # Obtener todas las propiedades de los nodos
            all_props = set()
            for _, attrs in G.nodes(data=True):
                all_props.update(attrs.keys())
            
            # Excluir propiedades problemáticas o que no se necesitan en Neo4j
            props_to_exclude = set(['shape', 'creado_desde_enlace'])
            clean_props = all_props - props_to_exclude
            
            # Crear encabezados
            headers = ['id:ID'] + list(clean_props) + [':LABEL']
            writer = csv.writer(f)
            writer.writerow(headers)
            
            # Escribir datos de nodos
            count = 0
            for node_id, attrs in G.nodes(data=True):
                row = [str(node_id)]  # Asegurar que el ID sea string
                
                # Agregar cada propiedad
                for prop in clean_props:
                    # Convertir valores a string y manejar None
                    val = attrs.get(prop, '')
                    if val is None:
                        val = ''
                    elif isinstance(val, (dict, list)):
                        val = json.dumps(val, ensure_ascii=False)
                    else:
                        val = str(val)
                    row.append(val)
                
                # Determinar el tipo de nodo (etiqueta)
                # Prioridad: 1. entity_type, 2. tipo, 3. detectar por patrón
                if 'entity_type' in attrs and attrs['entity_type']:
                    node_label = attrs['entity_type'].capitalize()
                elif 'tipo' in attrs:
                    if attrs['tipo'] == 'nunc':
                        node_label = 'NUNC'
                    elif attrs['tipo'] == 'persona':
                        node_label = 'Persona'
                    elif attrs['tipo'] == 'entidad':
                        node_label = 'Entidad'
                    else:
                        node_label = attrs['tipo'].capitalize()
                else:
                    # Detectar por patrón
                    node_id_str = str(node_id)
                    if node_id_str.isdigit() or (node_id_str.startswith("'") and node_id_str[1:].replace('-', '').isdigit()):
                        node_label = 'NUNC'
                    else:
                        node_label = 'Nodo'
                
                row.append(node_label)
                writer.writerow(row)
                
                count += 1
                if count % 10000 == 0:
                    self.stdout.write(f'  Procesados {count} nodos')
        
        # Escribir relaciones a CSV
        self.stdout.write('Exportando relaciones a CSV...')
        with open(rels_file, 'w', newline='', encoding='utf-8') as f:
            # Obtener todas las propiedades de las relaciones
            all_props = set()
            for _, _, attrs in G.edges(data=True):
                all_props.update(attrs.keys())
            
            # Excluir propiedades problemáticas
            props_to_exclude = set()  # Agregar aquí cualquier propiedad a excluir
            clean_props = all_props - props_to_exclude
            
            # Crear encabezados
            headers = [':START_ID', ':END_ID'] + list(clean_props) + [':TYPE']
            writer = csv.writer(f)
            writer.writerow(headers)
            
            # Escribir datos de relaciones
            count = 0
            for source, target, attrs in G.edges(data=True):
                # Asegurar que source y target sean strings
                row = [str(source), str(target)]
                
                # Agregar cada propiedad
                for prop in clean_props:
                    # Convertir valores a string y manejar None
                    val = attrs.get(prop, '')
                    if val is None:
                        val = ''
                    elif isinstance(val, (dict, list)):
                        val = json.dumps(val, ensure_ascii=False)
                    else:
                        val = str(val)
                    row.append(val)
                
                # Determinar el tipo de relación desde los atributos
                # Prioridad: 1. type, 2. tipo, 3. calidad_vinculo, 4. valor predeterminado
                if 'type' in attrs and attrs['type']:
                    rel_type = attrs['type'].replace(' ', '_').upper()
                elif 'tipo' in attrs and attrs['tipo']:
                    rel_type = attrs['tipo'].replace(' ', '_').upper()
                elif 'calidad_vinculo' in attrs and attrs['calidad_vinculo']:
                    rel_type = attrs['calidad_vinculo'].replace(' ', '_').upper()
                elif 'accion' in attrs and attrs['accion']:
                    rel_type = attrs['accion'].replace(' ', '_').upper()
                else:
                    rel_type = 'RELACIONADO'
                
                row.append(rel_type)
                writer.writerow(row)
                
                count += 1
                if count % 10000 == 0:
                    self.stdout.write(f'  Procesadas {count} relaciones')
        
        return nodes_file, rels_file