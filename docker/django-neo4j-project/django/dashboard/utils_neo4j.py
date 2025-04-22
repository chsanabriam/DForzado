import os
import pandas as pd
import networkx as nx
from networkx.algorithms.components import connected_components
from neo4j import GraphDatabase
from django.conf import settings
from .models import ConsolidadoSpoa, PersonasDf
from myproject.neo4j_driver import Neo4jConnection


def crear_red_desde_consolidado(ruta_archivo=None, chunksize=50000):
    """
    Crea una red no dirigida a partir de los datos del consolidado SPOA.
    Optimizada para archivos grandes de más de un millón de registros.
    
    Args:
        ruta_archivo: Ruta al archivo CSV opcional. Si no se proporciona, 
                      se usarán los datos ya cargados en los modelos.
        chunksize: Tamaño del chunk para procesar el CSV por lotes.
    
    Returns:
        G: El grafo de networkx creado
    """
    import time
    start_time = time.time()
    
    # Crear un grafo no dirigido
    G = nx.Graph()
    
    # Contador para mostrar progreso
    processed_rows = 0
    
    # Decidir si usar datos del archivo o de la base de datos
    if ruta_archivo and os.path.exists(ruta_archivo):
        print(f"Cargando datos desde el archivo: {ruta_archivo}")
        print(f"Usando chunksize de {chunksize} registros")
        
        # Primera pasada: agregar todos los nodos NUNC
        # Si solo se usa nunc se puede usar enumerate(pd.read_csv(ruta_archivo, chunksize=chunksize, usecols=['nunc'], sep="|"))
        # En caso contrario quitar la opción usecols
        print("Primera pasada: Agregando nodos NUNC...")
        for chunk_idx, chunk in enumerate(pd.read_csv(ruta_archivo, chunksize=chunksize, sep="|")):
            nunc_counter = 0
            for _, row in chunk.iterrows():
                nunc = str(row.get('nunc', '')).strip()
                necropsia = str(row.get('necropsia', '')).strip()
                seccional = str(row.get('seccional', '')).strip()
                unidad = str(row.get('unidad', '')).strip()
                despacho = str(row.get('despacho', '')).strip()
                fuente = str(row.get('fuente', '')).strip()
                if nunc and nunc not in G:
                    G.add_node(nunc, 
                                name=nunc, 
                                tipo='nunc', 
                                necropsia=necropsia,
                                seccional=seccional,
                                unidad=unidad,
                                despacho=despacho,
                                fuente=fuente
                            )
                    nunc_counter += 1
            
            processed_rows += len(chunk)
            print(f"Chunk {chunk_idx+1}: Procesados {processed_rows} registros, {nunc_counter} nodos NUNC agregados")
        
        print(f"Tiempo hasta ahora: {time.time() - start_time:.2f} segundos")
        print(f"Total de nodos NUNC: {sum(1 for n, d in G.nodes(data=True) if d.get('tipo') == 'nunc')}")
        
        # Segunda pasada: agregar nodos PERSONA y enlaces
        print("Segunda pasada: Agregando nodos PERSONA y enlaces...")
        processed_rows = 0
        persona_counter = 0
        edge_counter = 0
        
        # Diccionario para almacenar el nombre de las personas (evita duplicados)
        personas_nombres = {}
        
        for chunk_idx, chunk in enumerate(pd.read_csv(ruta_archivo, chunksize=chunksize, sep="|")):
            # Procesar el chunk
            for _, row in chunk.iterrows():
                nunc = str(row.get('nunc', '')).strip()
                numero_documento = str(row.get('numero_documento', '')).strip()
                nombre_completo = str(row.get('nombre_completo', '')).strip()
                calidad_vinculado = str(row.get('calidad_vinculado', '')).strip()
                
                if nunc and numero_documento:
                    # Guardar el nombre de la persona si no existe
                    if numero_documento not in personas_nombres:
                        personas_nombres[numero_documento] = nombre_completo
                        G.add_node(numero_documento, name=nombre_completo, tipo='persona')
                        persona_counter += 1
                    
                    # Crear enlace entre NUNC y PERSONA
                    if not G.has_edge(nunc, numero_documento):
                        G.add_edge(nunc, numero_documento, calidad_vinculo=calidad_vinculado)
                        edge_counter += 1
            
            processed_rows += len(chunk)
            print(f"Chunk {chunk_idx+1}: Procesados {processed_rows} registros, {persona_counter} nodos PERSONA, {edge_counter} enlaces")
        
        print(f"Tiempo hasta ahora: {time.time() - start_time:.2f} segundos")
        print(f"Total de nodos PERSONA: {sum(1 for n, d in G.nodes(data=True) if d.get('tipo') == 'persona')}")
        print(f"Total de enlaces: {len(G.edges())}")
        
    else:
        print("Cargando datos desde los modelos de Django")
        # Cargar datos desde los modelos de Django
        
        # Agregar nodos tipo NUNC
        total_nuncs = ConsolidadoSpoa.objects.count()
        print(f"Agregando {total_nuncs} nodos NUNC...")
        batch_size = 5000
        count = 0
        
        # Usar el método no_cache para evitar cargar todo en memoria
        for i in range(0, total_nuncs, batch_size):
            for spoa in ConsolidadoSpoa.objects.all()[i:i+batch_size]:
                G.add_node(spoa.nunc, 
                            name=spoa.nunc, 
                            tipo='nunc',
                            necropsia=spoa.necropsia,
                            seccional=spoa.seccional,
                            unidad=spoa.unidad,
                            despacho=spoa.despacho,
                            fuente=spoa.fuente
                        )
                count += 1
                if count % 10000 == 0:
                    print(f"Procesados {count} nodos NUNC")
        
        # Agregar nodos tipo PERSONA
        total_personas = PersonasDf.objects.count()
        print(f"Agregando {total_personas} nodos PERSONA...")
        count = 0
        
        for i in range(0, total_personas, batch_size):
            for persona in PersonasDf.objects.all()[i:i+batch_size]:
                G.add_node(persona.numero_identificacion, 
                           name=persona.nombre_completo,
                           tipo='persona')
                count += 1
                if count % 10000 == 0:
                    print(f"Procesados {count} nodos PERSONA")
        
        # Crear enlaces entre NUNC y PERSONA
        print("Creando enlaces...")
        count = 0
        edge_count = 0
        
        for i in range(0, total_nuncs, batch_size):
            for spoa in ConsolidadoSpoa.objects.all()[i:i+batch_size]:
                if spoa.numero_documento:
                    G.add_edge(spoa.nunc, 
                               spoa.numero_documento.numero_identificacion,
                               calidad_vinculo=spoa.calidad_vinculado or "")
                    edge_count += 1
                count += 1
                if count % 10000 == 0:
                    print(f"Procesados {count} registros, {edge_count} enlaces creados")
    
    print("Calculando componentes conectadas...")
    # Calcular componentes conectadas y asignarlas como atributo
    # Para grafos grandes, usamos una aproximación por lotes

    print("Creando diccionario para mapear componentes...")
    nodo_a_componente = {}

    # Para grafos muy grandes, podemos calcular componentes por lotes
    print("Calculando componentes...")
    if len(G) > 1000000:  # Para grafos extremadamente grandes
        # Paso 1: Obtener todas las componentes
        print("Grafo muy grande: calculando componentes progresivamente...")
        componentes = []
        for comp in connected_components(G):
            componentes.append(list(comp))
            if len(componentes) % 1000 == 0:
                print(f"Descubiertas {len(componentes)} componentes...")
        
        # Paso 2: Ordenar componentes por tamaño (de mayor a menor)
        print("Ordenando componentes por tamaño...")
        componentes_ordenadas = sorted(componentes, key=len, reverse=True)
        
        # Paso 3: Asignar índices a los nodos según el tamaño de su componente
        print("Asignando índices ordenados a los nodos...")
        for i, comp in enumerate(componentes_ordenadas):
            for nodo in comp:
                nodo_a_componente[nodo] = i
            
            if i % 1000 == 0 and i > 0:
                print(f"Procesadas {i} componentes ordenadas...")
    else:
        # Método estándar para grafos de tamaño moderado
        print("Calculando y ordenando componentes...")
        componentes = list(connected_components(G))
        
        # Ordenar componentes por tamaño (de mayor a menor)
        componentes_ordenadas = sorted(componentes, key=len, reverse=True)
        
        print(f"Se encontraron {len(componentes_ordenadas)} componentes")
        print(f"La componente más grande tiene {len(componentes_ordenadas[0])} nodos")
        
        for i, comp in enumerate(componentes_ordenadas):
            for nodo in comp:
                nodo_a_componente[nodo] = i
    
    print("Asignando componentes a los nodos...")
    # Asignar el número de componente como atributo a cada nodo
    nx.set_node_attributes(G, nodo_a_componente, 'componente')
    
    print("Calcular la centralidad de grado y el grado...")
    # Calcular diferentes métricas de centralidad
    # degree_centrality = nx.degree_centrality(G)
    degree = dict(nx.degree(G))
    
    # Asociar las métricas a los nodos como atributos
    # nx.set_node_attributes(G, degree_centrality, 'centralidad_grado')
    nx.set_node_attributes(G, degree, 'grado')
    
    # Calcular estadísticas finales
    num_componentes = len(set(nodo_a_componente.values()))
    tiempo_total = time.time() - start_time
    
    print(f"Red creada con {len(G.nodes)} nodos y {len(G.edges)} enlaces")
    print(f"Se identificaron {num_componentes} componentes conectadas")
    print(f"Tiempo total: {tiempo_total:.2f} segundos")
    
    return G


def guardar_red_en_neo4j(G, batch_size=5000, usar_transacciones=True):
    """
    Guarda la red de networkx en Neo4j de manera optimizada para grandes volúmenes.
    
    Args:
        G: Grafo de networkx a guardar
        batch_size: Tamaño del lote para las operaciones en Neo4j
        usar_transacciones: Si se deben usar transacciones explícitas (recomendado para grandes volúmenes)
    """
    import time
    start_time = time.time()
    
    # Obtener el driver de Neo4j
    driver = Neo4jConnection.get_driver()
    
    # Preparar nodos por tipo para procesamiento en lotes
    nodos_nunc = [(nid, attrs) for nid, attrs in G.nodes(data=True) if attrs.get('tipo') == 'nunc']
    nodos_persona = [(nid, attrs) for nid, attrs in G.nodes(data=True) if attrs.get('tipo') == 'persona']
    
    try:
        with driver.session() as session:
            # Limpiar la base de datos existente
            print("Limpiando base de datos Neo4j...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Crear índices para mejorar el rendimiento
            print("Creando índices...")
            session.run("CREATE INDEX IF NOT EXISTS FOR (n:NUNC) ON (n.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (n:Persona) ON (n.id)")
            
            # Usar Apoc si está disponible para cargas masivas
            apoc_disponible = False
            try:
                result = session.run("CALL apoc.help('apoc')")
                apoc_disponible = True
                print("APOC está disponible. Usaremos carga por lotes optimizada.")
            except Exception:
                print("APOC no está disponible. Usaremos método estándar.")
            
            # Método óptimo con APOC
            if apoc_disponible:
                # Crear nodos NUNC
                print(f"Creando {len(nodos_nunc)} nodos NUNC usando APOC...")
                for i in range(0, len(nodos_nunc), batch_size):
                    batch = nodos_nunc[i:i+batch_size]
                    
                    # Preparar datos para inserción masiva
                    data = [{"id": nid, "name": attrs.get('name', ''), 
                            "componente": attrs.get('componente', -1)} 
                           for nid, attrs in batch]
                    
                    # Inserción masiva con APOC
                    session.run("""
                    UNWIND $data AS row
                    CREATE (n:NUNC {id: row.id, name: row.name, componente: row.componente})
                    """, {"data": data})
                    
                    print(f"Procesados {min(i+batch_size, len(nodos_nunc))} de {len(nodos_nunc)} nodos NUNC")
                
                # Crear nodos PERSONA
                print(f"Creando {len(nodos_persona)} nodos PERSONA usando APOC...")
                for i in range(0, len(nodos_persona), batch_size):
                    batch = nodos_persona[i:i+batch_size]
                    
                    # Preparar datos para inserción masiva
                    data = [{"id": nid, "name": attrs.get('name', ''), 
                            "componente": attrs.get('componente', -1)} 
                           for nid, attrs in batch]
                    
                    # Inserción masiva con APOC
                    session.run("""
                    UNWIND $data AS row
                    CREATE (n:Persona {id: row.id, name: row.name, componente: row.componente})
                    """, {"data": data})
                    
                    print(f"Procesados {min(i+batch_size, len(nodos_persona))} de {len(nodos_persona)} nodos PERSONA")
                
                # Crear relaciones
                print(f"Creando {len(G.edges())} relaciones usando APOC...")
                enlaces = list(G.edges(data=True))
                
                for i in range(0, len(enlaces), batch_size):
                    batch = enlaces[i:i+batch_size]
                    
                    # Preparar datos para inserción masiva
                    data = [{"source": source, "target": target, 
                            "calidad_vinculo": attrs.get('calidad_vinculo', '')} 
                           for source, target, attrs in batch]
                    
                    # Inserción masiva con APOC
                    session.run("""
                    UNWIND $data AS row
                    MATCH (a), (b)
                    WHERE a.id = row.source AND b.id = row.target
                    CREATE (a)-[r:VINCULADO_A {calidad_vinculo: row.calidad_vinculo}]->(b)
                    """, {"data": data})
                    
                    print(f"Procesados {min(i+batch_size, len(enlaces))} de {len(enlaces)} relaciones")
            
            # Método estándar sin APOC
            else:
                # Función para procesar un lote de nodos
                def procesar_lote_nodos(nodos, tipo, tx=None):
                    for nodo_id, attrs in nodos:
                        if tipo == 'nunc':
                            cypher = """
                            MERGE (n:NUNC {id: $id})
                            SET n.name = $name,
                                n.componente = $componente
                            """
                        else:  # tipo 'persona'
                            cypher = """
                            MERGE (n:Persona {id: $id})
                            SET n.name = $name,
                                n.componente = $componente
                            """
                        
                        params = {
                            'id': nodo_id,
                            'name': attrs.get('name', ''),
                            'componente': attrs.get('componente', -1)
                        }
                        
                        if tx:
                            tx.run(cypher, params)
                        else:
                            session.run(cypher, params)
                
                # Crear nodos NUNC
                print(f"Creando {len(nodos_nunc)} nodos NUNC...")
                for i in range(0, len(nodos_nunc), batch_size):
                    batch = nodos_nunc[i:i+batch_size]
                    
                    if usar_transacciones:
                        with session.begin_transaction() as tx:
                            procesar_lote_nodos(batch, 'nunc', tx)
                    else:
                        procesar_lote_nodos(batch, 'nunc')
                    
                    print(f"Procesados {min(i+batch_size, len(nodos_nunc))} de {len(nodos_nunc)} nodos NUNC")
                
                # Crear nodos PERSONA
                print(f"Creando {len(nodos_persona)} nodos PERSONA...")
                for i in range(0, len(nodos_persona), batch_size):
                    batch = nodos_persona[i:i+batch_size]
                    
                    if usar_transacciones:
                        with session.begin_transaction() as tx:
                            procesar_lote_nodos(batch, 'persona', tx)
                    else:
                        procesar_lote_nodos(batch, 'persona')
                    
                    print(f"Procesados {min(i+batch_size, len(nodos_persona))} de {len(nodos_persona)} nodos PERSONA")
                
                # Función para procesar un lote de relaciones
                def procesar_lote_relaciones(enlaces, tx=None):
                    for source, target, attrs in enlaces:
                        cypher = """
                        MATCH (a), (b)
                        WHERE a.id = $source AND b.id = $target
                        MERGE (a)-[r:VINCULADO_A {calidad_vinculo: $calidad_vinculo}]->(b)
                        """
                        
                        params = {
                            'source': source,
                            'target': target,
                            'calidad_vinculo': attrs.get('calidad_vinculo', '')
                        }
                        
                        if tx:
                            tx.run(cypher, params)
                        else:
                            session.run(cypher, params)
                
                # Crear relaciones
                print(f"Creando {len(G.edges())} relaciones...")
                enlaces = list(G.edges(data=True))
                
                for i in range(0, len(enlaces), batch_size):
                    batch = enlaces[i:i+batch_size]
                    
                    if usar_transacciones:
                        with session.begin_transaction() as tx:
                            procesar_lote_relaciones(batch, tx)
                    else:
                        procesar_lote_relaciones(batch)
                    
                    print(f"Procesados {min(i+batch_size, len(enlaces))} de {len(enlaces)} relaciones")
        
        tiempo_total = time.time() - start_time
        print(f"Red guardada en Neo4j con {len(G.nodes)} nodos y {len(G.edges)} enlaces")
        print(f"Tiempo total: {tiempo_total:.2f} segundos")
    
    except Exception as e:
        print(f"Error al guardar la red en Neo4j: {str(e)}")
        raise

def calcular_metricas_centralidad(G):
    """
    Calcula métricas de centralidad para el grafo y devuelve un diccionario
    con los resultados.
    
    Args:
        G: Grafo de networkx
        
    Returns:
        dict: Diccionario con métricas de centralidad
    """
    print("Calculando métricas de centralidad...")
    
    # Calcular diferentes métricas de centralidad
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    
    # Asociar las métricas a los nodos como atributos
    nx.set_node_attributes(G, degree_centrality, 'degree_centrality')
    nx.set_node_attributes(G, betweenness_centrality, 'betweenness_centrality')
    nx.set_node_attributes(G, closeness_centrality, 'closeness_centrality')
    
    # Encontrar los nodos más centrales según diferentes métricas
    top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    top_closeness = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Estadísticas generales del grafo
    stats = {
        'num_nodos': len(G.nodes),
        'num_enlaces': len(G.edges),
        'num_componentes': len(list(connected_components(G))),
        'densidad': nx.density(G),
        'diametro': nx.diameter(G) if nx.is_connected(G) else None,
        'top_degree': top_degree,
        'top_betweenness': top_betweenness,
        'top_closeness': top_closeness
    }
    
    return stats


def actualizar_metricas_en_neo4j(G):
    """
    Actualiza las métricas de centralidad en la base de datos Neo4j.
    
    Args:
        G: Grafo de networkx con métricas calculadas
    """
    # Obtener el driver de Neo4j
    driver = Neo4jConnection.get_driver()
    
    with driver.session() as session:
        try:
            print("Actualizando métricas en Neo4j...")
            
            # Actualizar métricas para cada nodo
            for nodo_id, attrs in G.nodes(data=True):
                cypher = """
                MATCH (n)
                WHERE n.id = $id
                SET n.degree_centrality = $degree_centrality,
                    n.betweenness_centrality = $betweenness_centrality,
                    n.closeness_centrality = $closeness_centrality
                """
                
                session.run(cypher, {
                    'id': nodo_id,
                    'degree_centrality': attrs.get('degree_centrality', 0),
                    'betweenness_centrality': attrs.get('betweenness_centrality', 0),
                    'closeness_centrality': attrs.get('closeness_centrality', 0)
                })
            
            print("Métricas actualizadas en Neo4j")
        
        except Exception as e:
            print(f"Error al actualizar métricas en Neo4j: {str(e)}")
            raise


def ejecutar_flujo_completo(ruta_archivo=None, calcular_metricas=True):
    """
    Ejecuta el flujo completo: crear red, calcular métricas y guardar en Neo4j.
    
    Args:
        ruta_archivo: Ruta al archivo CSV opcional
        calcular_metricas: Si se deben calcular y guardar métricas de centralidad
    """
    # Crear la red
    G = crear_red_desde_consolidado(ruta_archivo)
    
    # Calcular métricas si se solicita
    if calcular_metricas:
        try:
            metricas = calcular_metricas_centralidad(G)
            print("Métricas calculadas:", metricas)
        except Exception as e:
            print(f"Error al calcular métricas: {str(e)}")
            # Continuamos aunque falle el cálculo de métricas
    
    # Guardar en Neo4j
    guardar_red_en_neo4j(G)
    
    # Actualizar métricas en Neo4j si se calcularon
    if calcular_metricas:
        try:
            actualizar_metricas_en_neo4j(G)
        except Exception as e:
            print(f"Error al actualizar métricas en Neo4j: {str(e)}")
    
    return G