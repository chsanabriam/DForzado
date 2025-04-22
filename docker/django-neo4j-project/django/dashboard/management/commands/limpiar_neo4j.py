# dashboard/management/commands/limpiar_neo4j.py
from django.core.management.base import BaseCommand
from myproject.neo4j_driver import Neo4jConnection

class Command(BaseCommand):
    help = 'Elimina todos los nodos y relaciones de Neo4j'

    def handle(self, *args, **options):
        driver = Neo4jConnection.get_driver()
        
        try:
            
            with driver.session() as session:
                result = session.run("MATCH (n) DETACH DELETE n")
                self.stdout.write(self.style.SUCCESS('Base de datos Neo4j limpiada exitosamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al limpiar Neo4j: {str(e)}'))
        finally:
            None