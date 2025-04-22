import os
from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.utils import cargar_consolidado_spoa, cargar_personas_df, cargar_rud
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
        parser.add_argument(
            '--rud',
            action='store_true',
            help='Cargar sólo datos del Registro Unido de Desaparecidos',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Obtener la ruta base de la app dashboard
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_folder = os.path.join(app_path, 'data')
        
        self.stdout.write(self.style.SUCCESS(f'Buscando archivos CSV en: {data_folder}'))
        
        # Nombres de los archivos
        consolidado_file = os.path.join(data_folder, "consolidado_df_delitos_relacionados_2025-04-22.csv")
        personas_file = os.path.join(data_folder, "personas_delitos_2025-04-21.csv")
        rud_file = os.path.join(data_folder, "rud_dforzada_2025-04-21.csv")
        
        # Verificar que los archivos existan
        if not os.path.exists(consolidado_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {consolidado_file}'))
        
        if not os.path.exists(personas_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {personas_file}'))
        
        if not os.path.exists(rud_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {rud_file}'))
        
        # Determinar si no se especificó ninguna opción específica
        ninguna_opcion = not (options['consolidado'] or options['personas'] or options['rud'])
        
        # Cargar consolidado SPOA si se solicita o si no se especifica ninguna opción
        if options['consolidado'] or ninguna_opcion:
            try:
                self.stdout.write(self.style.WARNING('Cargando datos de consolidado SPOA...'))
                contador = cargar_consolidado_spoa(consolidado_file)
                self.stdout.write(self.style.SUCCESS(f'Se cargaron {contador} registros en ConsolidadoSpoa'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al cargar datos de consolidado: {str(e)}'))
        
        # Cargar personas si se solicita o si no se especifica ninguna opción
        if options['personas'] or ninguna_opcion:
            try:
                self.stdout.write(self.style.WARNING('Cargando datos de personas...'))
                contador = cargar_personas_df(personas_file)
                self.stdout.write(self.style.SUCCESS(f'Se cargaron {contador} registros en PersonasDf'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al cargar datos de personas: {str(e)}'))
                
        # Cargar datos del RUD si se solicita o si no se especifica ninguna opción
        if options['rud'] or ninguna_opcion:
            try:
                self.stdout.write(self.style.WARNING('Cargando datos del Registro Unido de Desaparecidos...'))
                contador = cargar_rud(rud_file)
                self.stdout.write(self.style.SUCCESS(f'Se cargaron {contador} registros en RegistroUnidoDesaparecidos'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al cargar datos del RUD: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Proceso de carga de datos completado'))
        self.stdout.write(self.style.SUCCESS('Proceso de carga de datos completado'))