import os
from django.core.management.base import BaseCommand
from dashboard.utils_neo4j import crear_red_desde_consolidado, guardar_red_en_neo4j, calcular_metricas_centralidad


class Command(BaseCommand):
    help = 'Crear red de NUNC y Personas y guardarla en Neo4j (Optimizado para archivos grandes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--archivo',
            help='Ruta al archivo CSV de consolidado. Si no se proporciona, se usarán los datos de la base de datos.',
        )
        parser.add_argument(
            '--sin-metricas',
            action='store_true',
            help='No calcular métricas de centralidad (más rápido para redes grandes)',
        )
        parser.add_argument(
            '--chunksize',
            type=int,
            default=50000,
            help='Tamaño del chunk para procesar el CSV (default: 50000)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5000,
            help='Tamaño del lote para operaciones en Neo4j (default: 5000)',
        )
        parser.add_argument(
            '--solo-red',
            action='store_true',
            help='Solo crear la red en memoria sin guardarla en Neo4j',
        )
        parser.add_argument(
            '--solo-guardar',
            action='store_true',
            help='Solo guardar la red en Neo4j (la red debe existir en memoria)',
        )

    def handle(self, *args, **options):
        import time
        tiempo_inicio = time.time()
        
        archivo = options.get('archivo')
        calcular_metricas = not options.get('sin_metricas')
        chunksize = options.get('chunksize')
        batch_size = options.get('batch_size')
        solo_red = options.get('solo_red')
        solo_guardar = options.get('solo_guardar')
        
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('Iniciando creación y almacenamiento de red en Neo4j'))
        self.stdout.write(self.style.SUCCESS('='*80))
        
        if archivo:
            if os.path.exists(archivo):
                self.stdout.write(self.style.SUCCESS(f'Usando archivo: {archivo}'))
            else:
                self.stdout.write(self.style.ERROR(f'El archivo no existe: {archivo}'))
                return
        else:
            self.stdout.write(self.style.SUCCESS('Usando datos de la base de datos'))
        
        self.stdout.write(self.style.SUCCESS(f'Tamaño de chunk para CSV: {chunksize}'))
        self.stdout.write(self.style.SUCCESS(f'Tamaño de lote para Neo4j: {batch_size}'))
        
        if calcular_metricas:
            self.stdout.write(self.style.SUCCESS('Se calcularán métricas de centralidad'))
        else:
            self.stdout.write(self.style.SUCCESS('No se calcularán métricas de centralidad'))
        
        try:
            # Crear la red (a menos que solo estemos guardando)
            if not solo_guardar:
                self.stdout.write(self.style.SUCCESS('Creando la red...'))
                G = crear_red_desde_consolidado(archivo, chunksize=chunksize)
                tiempo_creacion = time.time() - tiempo_inicio
                self.stdout.write(self.style.SUCCESS(f'Red creada en {tiempo_creacion:.2f} segundos'))
                
                # Guardar la red para uso futuro
                import pickle
                with open('red_consolidado.pickle', 'wb') as f:
                    pickle.dump(G, f)
                self.stdout.write(self.style.SUCCESS('Red guardada en archivo red_consolidado.pickle'))
            else:
                # Cargar la red previamente guardada
                import pickle
                try:
                    with open('red_consolidado.pickle', 'rb') as f:
                        G = pickle.load(f)
                    self.stdout.write(self.style.SUCCESS('Red cargada desde archivo red_consolidado.pickle'))
                except FileNotFoundError:
                    self.stdout.write(self.style.ERROR('No se encontró el archivo red_consolidado.pickle'))
                    self.stdout.write(self.style.ERROR('Primero debes crear la red con --solo-red'))
                    return
            
            # Si solo queríamos crear la red, terminamos aquí
            if solo_red:
                self.stdout.write(self.style.SUCCESS('Proceso finalizado (solo creación de red)'))
                return
            
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
            
            # Guardar en Neo4j
            tiempo_neo4j_inicio = time.time()
            self.stdout.write(self.style.SUCCESS('Guardando red en Neo4j...'))
            guardar_red_en_neo4j(G, batch_size=batch_size)
            tiempo_neo4j = time.time() - tiempo_neo4j_inicio
            
            # Tiempo total
            tiempo_total = time.time() - tiempo_inicio
            
            self.stdout.write(self.style.SUCCESS('='*80))
            self.stdout.write(self.style.SUCCESS(f'Resumen de tiempos:'))
            if not solo_guardar:
                self.stdout.write(self.style.SUCCESS(f'- Creación de red: {tiempo_creacion:.2f} segundos'))
            if calcular_metricas and not solo_red:
                self.stdout.write(self.style.SUCCESS(f'- Cálculo de métricas: {tiempo_metricas:.2f} segundos'))
            self.stdout.write(self.style.SUCCESS(f'- Guardado en Neo4j: {tiempo_neo4j:.2f} segundos'))
            self.stdout.write(self.style.SUCCESS(f'- Tiempo total: {tiempo_total:.2f} segundos'))
            self.stdout.write(self.style.SUCCESS('='*80))
            
            self.stdout.write(self.style.SUCCESS('Proceso completado exitosamente'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise