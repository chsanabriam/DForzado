import os
from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.utils import (
    cargar_consolidado_spoa,
    cargar_personas_df,
    cargar_rud,
    cargar_perfiles_personas,
    cargar_aparecidos_vivos_no_registrados,
    cargar_funcionarios
)
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
        
        parser.add_argument(
            '--perfiles',
            action='store_true',
            help='Cargar sólo perfiles de personas',
        )
        
        parser.add_argument(
            '--aparecidos',
            action='store_true',
            help='Cargar sólo datos de aparecidos vivos no registrados',
        )
        
        parser.add_argument(
            '--funcionarios',
            action='store_true',
            help='Cargar sólo datos de funcionarios',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Obtener la ruta base de la app dashboard
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_folder = os.path.join(app_path, 'data')
        
        self.stdout.write(self.style.SUCCESS(f'Buscando archivos CSV en: {data_folder}'))
        
        # Nombres de los archivos
        consolidado_file = os.path.join(data_folder, "consolidado_df_delitos_relacionados_2025-05-20.csv")
        personas_file = os.path.join(data_folder, "personas_delitos_2025-05-20.csv")
        rud_file = os.path.join(data_folder, "rud_dforzada_2025-04-21.csv")
        perfiles_file = os.path.join(data_folder, "lote_completo_v2.json")
        aparecidos_file = os.path.join(data_folder, "Reporte_3_Aparecidos_vivos_no_registrados_2025-05-13.csv")
        funcionarios_file = os.path.join(data_folder, "funcionarios_exfuncionarios.csv")
        
        # Verificar que los archivos existan
        if not os.path.exists(consolidado_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {consolidado_file}'))
        
        if not os.path.exists(personas_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {personas_file}'))
        
        if not os.path.exists(rud_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {rud_file}'))
            
        if not os.path.exists(perfiles_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {perfiles_file}'))
            
        if not os.path.exists(aparecidos_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {aparecidos_file}'))
            
        if not os.path.exists(funcionarios_file):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {funcionarios_file}'))
        
        # Determinar si no se especificó ninguna opción específica
        ninguna_opcion = not (options['consolidado'] 
                              or options['personas'] 
                              or options['rud'] 
                              or options['perfiles'] 
                              or options['aparecidos']
                              or options['funcionarios'])
        
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
                
        # Cargar perfiles de personas si se solicita o si no se especifica ninguna opción
        if options['perfiles'] or ninguna_opcion:
            try:
                self.stdout.write(self.style.WARNING('Cargando perfiles de personas...'))
                contador = cargar_perfiles_personas(perfiles_file)
                self.stdout.write(self.style.SUCCESS(f'Se cargaron {contador} perfiles en PerfilPersona'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al cargar perfiles de personas: {str(e)}'))
        
        # Cargar datos de aparecidos vivos no registrados si se solicita o si no se especifica ninguna opción
        if options['aparecidos'] or ninguna_opcion:
            try:
                self.stdout.write(self.style.WARNING('Cargando datos de aparecidos vivos no registrados...'))
                contador = cargar_aparecidos_vivos_no_registrados(aparecidos_file)
                self.stdout.write(self.style.SUCCESS(f'Se cargaron {contador} registros en AparecidosVivosNoRegistrados'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al cargar datos de aparecidos vivos no registrados: {str(e)}'))
        
        #  Cargar datos de funcionarios si se solicita o si no se especifica ninguna opción
        if options['funcionarios'] or ninguna_opcion:
            try:
                self.stdout.write(self.style.WARNING('Cargando datos de funcionarios...'))
                contador = cargar_funcionarios(funcionarios_file)
                self.stdout.write(self.style.SUCCESS(f'Se cargaron {contador} registros en Funcionario'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al cargar datos de funcionarios: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Proceso de carga de datos completado'))
