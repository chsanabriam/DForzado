import os
from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.utils import cargar_consolidado_spoa, cargar_personas_df
from django.db import transaction


class Command(BaseCommand):
    help = 'Carga datos desde archivos CSV a los modelos correspondientes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--consolidado',
            action='store_true',
            help='Cargar sólo datos de consolidado SPOA',
        )
        parser.add_argument(
            '--personas',
            action='store_true',
            help='Cargar sólo datos de personas',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Obtener la ruta base de la app dashboard
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_folder = os.path.join(app_path, 'data')
        
        self.stdout.write(self.style.SUCCESS(f'Buscando archivos CSV en: {data_folder}'))
        
        # Nombres de los archivos
        consolidado_file = os.path.join(data_folder, "consolidado_delitos_2025-04-09.csv")
        personas_file = os.path.join(data_folder, "personas_delitos_2025-04-09.csv")
        
        # Verificar que los archivos existan
        if not os.path.exists(consolidado_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {consolidado_file}'))
        
        if not os.path.exists(personas_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {personas_file}'))
        
        # Cargar consolidado SPOA si se solicita o si no se especifica ninguna opción
        if options['consolidado'] or (not options['consolidado'] and not options['personas']):
            try:
                self.stdout.write(self.style.WARNING('Cargando datos de consolidado SPOA...'))
                contador = cargar_consolidado_spoa(consolidado_file)
                self.stdout.write(self.style.SUCCESS(f'Se cargaron {contador} registros en ConsolidadoSpoa'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al cargar datos de consolidado: {str(e)}'))
        
        # Cargar personas si se solicita o si no se especifica ninguna opción
        if options['personas'] or (not options['consolidado'] and not options['personas']):
            try:
                self.stdout.write(self.style.WARNING('Cargando datos de personas...'))
                contador = cargar_personas_df(personas_file)
                self.stdout.write(self.style.SUCCESS(f'Se cargaron {contador} registros en PersonasDf'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al cargar datos de personas: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Proceso de carga de datos completado'))