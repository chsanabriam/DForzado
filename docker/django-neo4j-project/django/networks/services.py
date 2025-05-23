import time
from myproject.neo4j_driver import get_neo4j_session, execute_query


def get_component_info(node_id, limit=1000):
    """
    Obtiene información sobre la componente a la que pertenece un nodo
    
    Args:
        node_id: ID del nodo a consultar
        limit: Límite de nodos a devolver
        
    Returns:
        dict: Información de la componente
    """
    start_time = time.time()
    
    # Obtener componente del nodo
    componente_query = """
    MATCH (n {id: $node_id})
    RETURN n.componente as componente
    """
    
    componente_result = execute_query(componente_query, {'node_id': node_id})
    
    if not componente_result:
        return {
            'error': 'Nodo no encontrado',
            'execution_time': time.time() - start_time
        }
    
    componente = componente_result[0].get('componente')
    
    # # Consultar nodos de la misma componente
    # nodes_query = """
    # MATCH (n)
    # WHERE n.componente = $componente
    # RETURN n.id as id, n.name as name, labels(n)[0] as type, n.componente as componente
    # LIMIT $limit
    # """
    
    # Consultar nodos de la misma componente
    nodes_query = """
    MATCH (n)
    WHERE n.componente = $componente
    RETURN n.id as id, n.name as name, n.tipo as type, n.componente as componente, n.color as color
    LIMIT $limit
    """
    
    nodes_result = execute_query(nodes_query, {'componente': componente, 'limit': limit})
    
    # Obtener las relaciones entre estos nodos
    # Consulta modificada para evitar duplicados
    relationships_query = """
    MATCH (n)-[r]-(m)
    WHERE n.componente = $componente AND m.componente = $componente
    AND id(n) < id(m)  // Esta condición asegura que cada relación se cuente una sola vez
    RETURN n.id as source, m.id as target, type(r) as type, 
        CASE WHEN r.calidad_vinculo IS NOT NULL THEN r.calidad_vinculo ELSE '' END as calidad_vinculo
    LIMIT $limit
    """
    
    relationships_result = execute_query(relationships_query, {'componente': componente, 'limit': limit*2})
    
    # Formatear resultados para visualización
    nodes = []
    node_ids = set()
    for record in nodes_result:
        print(record.keys())
        if record['id'] not in node_ids:
            node_type = record['type']
            # node_color = '#1f77b4' if node_type == 'Persona' else '#ff7f0e'  # Azul para personas, naranja para NUNC
            node_color = '#ff7f0e' if node_type == 'entidad' else record['color']
            
            nodes.append({
                'id': record['id'],
                'label': record['name'],
                'name': record['name'],
                'color': node_color,
                'size': 5,
                'type': node_type
            })
            node_ids.add(record['id'])
    
    edges = []
    edge_keys = set()
    for record in relationships_result:
        edge_key = f"{record['source']}-{record['target']}"
        if edge_key not in edge_keys:
            edges.append({
                'from': record['source'],
                'to': record['target'],
                'label': record['calidad_vinculo'],
                'arrows': 'to'
            })
            edge_keys.add(edge_key)
    
    # Guardar registro de la consulta
    execution_time = time.time() - start_time
    
    return {
        'componente': componente,
        'nodes': nodes,
        'edges': edges,
        'node_count': len(nodes),
        'edge_count': len(edges),
        'execution_time': execution_time,
        'limit_reached': len(nodes) >= limit
    }

def get_neighbors(node_id, depth=1, limit=100):
    """
    Obtiene los vecinos de un nodo hasta una profundidad determinada
    
    Args:
        node_id: ID del nodo a consultar
        depth: Profundidad de la búsqueda
        limit: Límite de nodos a devolver
        
    Returns:
        dict: Información de los vecinos
    """
    start_time = time.time()
    
    # Consulta para obtener vecinos
    query = """
    MATCH path = (n {id: $node_id})-[*1..{depth}]-(neighbor)
    WITH n, neighbor, [r IN relationships(path) | r] as rels
    RETURN n.id as source_id, n.name as source_name, labels(n)[0] as source_type,
           neighbor.id as neighbor_id, neighbor.name as neighbor_name, labels(neighbor)[0] as neighbor_type,
           [r IN rels | {type: type(r), properties: properties(r)}] as relationships
    LIMIT $limit
    """
    
    result = execute_query(query, {'node_id': node_id, 'depth': depth, 'limit': limit})
    
    # Formatear resultados
    nodes = []
    node_ids = set()
    edges = []
    edge_keys = set()
    
    # Agregar nodo central
    if result:
        source_id = result[0]['source_id']
        source_name = result[0]['source_name']
        source_type = result[0]['source_type']
        
        nodes.append({
            'id': source_id,
            'label': source_name,
            'color': '#ff0000',  # Rojo para el nodo central
            'size': 8,
            'type': source_type
        })
        node_ids.add(source_id)
    
    # Agregar vecinos y relaciones
    for record in result:
        neighbor_id = record['neighbor_id']
        
        # Agregar nodo vecino si no existe
        if neighbor_id not in node_ids:
            neighbor_type = record['neighbor_type']
            node_color = '#1f77b4' if neighbor_type == 'Persona' else '#ff7f0e'
            
            nodes.append({
                'id': neighbor_id,
                'label': record['neighbor_name'],
                'color': node_color,
                'size': 5,
                'type': neighbor_type
            })
            node_ids.add(neighbor_id)
        
        # Agregar relaciones
        for rel in record['relationships']:
            edge_from = record['source_id']
            edge_to = record['neighbor_id']
            edge_key = f"{edge_from}-{edge_to}"
            
            if edge_key not in edge_keys:
                calidad_vinculo = rel['properties'].get('calidad_vinculo', '')
                
                edges.append({
                    'from': edge_from,
                    'to': edge_to,
                    'label': calidad_vinculo,
                    'arrows': 'to'
                })
                edge_keys.add(edge_key)
    
    # Guardar registro de la consulta
    execution_time = time.time() - start_time
    
    return {
        'nodes': nodes,
        'edges': edges,
        'node_count': len(nodes),
        'edge_count': len(edges),
        'execution_time': execution_time,
        'limit_reached': len(result) >= limit
    }