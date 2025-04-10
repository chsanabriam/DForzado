# myproject/neo4j_driver.py
import os
from neo4j import GraphDatabase
from django.conf import settings

class Neo4jConnection:
    _driver = None

    @classmethod
    def get_driver(cls):
        # Implementación del patrón Singleton para el driver de Neo4j
        if cls._driver is None:
            uri = settings.NEO4J_URI
            user = settings.NEO4J_USER
            password = settings.NEO4J_PASSWORD
            
            cls._driver = GraphDatabase.driver(uri, auth=(user, password))
            
            # Verificar conexión
            try:
                cls._driver.verify_connectivity()
                print("Conexión a Neo4j establecida con éxito.")
            except Exception as e:
                print(f"Error al conectar con Neo4j: {e}")
                raise
                
        return cls._driver

    @classmethod
    def close(cls):
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None
            print("Conexión a Neo4j cerrada.")

# Función para obtener una sesión de Neo4j
def get_neo4j_session():
    driver = Neo4jConnection.get_driver()
    return driver.session()

# Ejemplo de consulta a Neo4j
def execute_query(query, params=None):
    with get_neo4j_session() as session:
        result = session.run(query, params)
        return [record for record in result]

# Ejemplo de uso:
# from myproject.neo4j_driver import execute_query
# 
# def get_all_users():
#     query = "MATCH (u:User) RETURN u.name as name, u.email as email"
#     return execute_query(query)