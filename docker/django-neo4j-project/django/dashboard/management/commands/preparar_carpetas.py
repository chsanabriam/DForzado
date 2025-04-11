import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Crea la estructura de carpetas necesaria para la app dashboard'

    def handle(self, *args, **options):
        # Obtener la ruta base de la app dashboard
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Carpetas a crear
        carpetas = [
            os.path.join(app_path, 'data'),
            os.path.join(app_path, 'management'),
            os.path.join(app_path, 'management', 'commands'),
            os.path.join(app_path, 'static', 'dashboard', 'css'),
            os.path.join(app_path, 'static', 'dashboard', 'js'),
            os.path.join(app_path, 'static', 'dashboard', 'img'),
        ]
        
        for carpeta in carpetas:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)
                self.stdout.write(self.style.SUCCESS(f'Carpeta creada: {carpeta}'))
            else:
                self.stdout.write(self.style.WARNING(f'La carpeta ya existe: {carpeta}'))
        
        # Crear archivo __init__.py en carpetas de management
        init_files = [
            os.path.join(app_path, 'management', '__init__.py'),
            os.path.join(app_path, 'management', 'commands', '__init__.py'),
        ]
        
        for init_file in init_files:
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('')
                self.stdout.write(self.style.SUCCESS(f'Archivo creado: {init_file}'))
            else:
                self.stdout.write(self.style.WARNING(f'El archivo ya existe: {init_file}'))
        
        # Mostrar mensaje sobre dónde colocar los archivos CSV
        data_folder = os.path.join(app_path, 'data')
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('INSTRUCCIONES'))
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS(f'Por favor, coloca los archivos CSV en la carpeta:'))
        self.stdout.write(self.style.SUCCESS(f'{data_folder}'))
        self.stdout.write(self.style.SUCCESS('Los archivos deben llamarse:'))
        self.stdout.write(self.style.SUCCESS('  - consolidado_delitos_2025-04-09.csv'))
        self.stdout.write(self.style.SUCCESS('  - personas_delitos_2025-04-09.csv'))
        self.stdout.write(self.style.SUCCESS('='*80))