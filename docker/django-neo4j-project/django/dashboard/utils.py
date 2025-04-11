import pandas as pd
import csv
import os
from datetime import datetime
from django.db import transaction
from .models import ConsolidadoSpoa, PersonasDf

def parse_date(date_str):
    """
    Convierte una cadena de fecha en un objeto datetime
    Intenta diferentes formatos de fecha
    """
    if not date_str or pd.isna(date_str):
        return None
    
    # Formatos de fecha comunes en datos colombianos
    formats = [
        '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y',
        '%Y/%m/%d', '%d.%m.%Y', '%Y.%m.%d'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    
    return None

@transaction.atomic
def cargar_consolidado_spoa(ruta_archivo):
    """
    Carga datos desde un archivo CSV al modelo ConsolidadoSpoa
    
    Args:
        ruta_archivo: Ruta al archivo CSV que contiene los datos
        
    Returns:
        int: Número de registros cargados
    """
    # Verificar que el archivo existe
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo {ruta_archivo} no existe")
    
    # Si el archivo es muy grande, usar chunks con pandas
    chunksize = 10000
    counter = 0
    
    # Verificar la extensión del archivo
    _, extension = os.path.splitext(ruta_archivo)
    
    if extension.lower() == '.csv':
        # Leer el archivo en chunks para manejar archivos grandes
        for chunk in pd.read_csv(ruta_archivo, chunksize=chunksize, sep="|"):
            registros = []
            
            for _, row in chunk.iterrows():
                # Crear objeto pero no guardar aún (bulk_create es más eficiente)
                registro = ConsolidadoSpoa(
                    nunc=str(row.get('nunc', '')).strip(),
                    fecha_hechos=parse_date(row.get('fecha_hechos')),
                    fecha_denuncia=parse_date(row.get('fecha_denuncia')),
                    seccional=str(row.get('seccional', '')).strip(),
                    unidad=str(row.get('unidad', '')).strip(),
                    despacho=str(row.get('despacho', '')).strip(),
                    numero_documento=str(row.get('numero_documento', '')).strip(),
                    nombre_completo=str(row.get('nombre_completo', '')).strip(),
                    relato=str(row.get('relato', '')),
                    delito=str(row.get('delito', '')).strip(),
                    grupo_delito=str(row.get('grupo_delito', '')).strip(),
                    necropsia=str(row.get('necropsia', '')).strip(),
                    fuente=str(row.get('fuente', '')).strip(),
                    calidad_vinculado=str(row.get('calidad_vinculado', '')).strip()
                )
                registros.append(registro)
            
            # Insertar en bulk (mucho más eficiente que uno por uno)
            # El parámetro ignore_conflicts evita errores por duplicados
            ConsolidadoSpoa.objects.bulk_create(registros, ignore_conflicts=True)
            counter += len(registros)
            
        return counter
    else:
        raise ValueError(f"Formato de archivo no soportado: {extension}")

@transaction.atomic
def cargar_personas_df(ruta_archivo):
    """
    Carga datos desde un archivo CSV al modelo PersonasDf
    Debe ejecutarse ANTES de cargar_consolidado_spoa
    
    Args:
        ruta_archivo: Ruta al archivo CSV que contiene los datos
        
    Returns:
        int: Número de registros cargados
    """
    # Verificar que el archivo existe
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo {ruta_archivo} no existe")
    
    # Si el archivo es muy grande, usar chunks con pandas
    chunksize = 10000
    counter = 0
    
    # Verificar la extensión del archivo
    _, extension = os.path.splitext(ruta_archivo)
    
    if extension.lower() == '.csv':
        # Leer el archivo en chunks para manejar archivos grandes
        for chunk in pd.read_csv(ruta_archivo, chunksize=chunksize, sep="|"):
            registros = []
            
            for _, row in chunk.iterrows():
                # Convertir valores a booleanos correctamente:
                # Si el valor es 1, debe ser True; si es 0, debe ser False
                desaparicion = row.get('desaparicion_forzada', 0)
                homicidio = row.get('homicidio', 0)
                secuestro = row.get('secuestro', 0)
                reclutamiento = row.get('reclutamiento_ilicito', 0)
                
                # Asegurarse de que los valores sean enteros o booleanos antes de la conversión
                if not pd.isna(desaparicion):
                    desaparicion = int(desaparicion) == 1
                else:
                    desaparicion = False
                    
                if not pd.isna(homicidio):
                    homicidio = int(homicidio) == 1
                else:
                    homicidio = False
                    
                if not pd.isna(secuestro):
                    secuestro = int(secuestro) == 1
                else:
                    secuestro = False
                    
                if not pd.isna(reclutamiento):
                    reclutamiento = int(reclutamiento) == 1
                else:
                    reclutamiento = False
                
                registro = PersonasDf(
                    numero_identificacion=str(row.get('numero_documento', '')).strip(),
                    nombre_completo=str(row.get('nombre_completo', '')).strip(),
                    desaparcion_forzada=desaparicion,
                    homicidio=homicidio,
                    secuestro=secuestro,
                    reclutamiento_ilicito=reclutamiento
                )
                registros.append(registro)
            
            # Insertar en bulk (mucho más eficiente que uno por uno)
            # El parámetro ignore_conflicts evita errores por duplicados
            PersonasDf.objects.bulk_create(registros, ignore_conflicts=True)
            counter += len(registros)
            
        return counter
    else:
        raise ValueError(f"Formato de archivo no soportado: {extension}")

def obtener_distribucion_por_fuente():
    """
    Obtiene la distribución de registros por fuente
    
    Returns:
        dict: Diccionario con las fuentes como claves y la cantidad como valores
    """
    from django.db.models import Count
    return list(ConsolidadoSpoa.objects.values('fuente')
                .annotate(cantidad=Count('fuente'))
                .order_by('-cantidad'))

def obtener_distribucion_por_unidad():
    """
    Obtiene la distribución de registros por unidad
    
    Returns:
        dict: Diccionario con las unidades como claves y la cantidad como valores
    """
    from django.db.models import Count
    return list(ConsolidadoSpoa.objects.values('unidad')
                .annotate(cantidad=Count('unidad'))
                .order_by('-cantidad'))