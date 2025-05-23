import pandas as pd
import csv
import os
import json
from datetime import datetime
from django.db import transaction, IntegrityError
from .models import ConsolidadoSpoa, PersonasDf, RegistroUnicoDesaparecidos, PerfilPersona, AparecidosVivosNoRegistrados, Funcionario

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
        for chunk in pd.read_csv(ruta_archivo, chunksize=chunksize, sep="|", dtype={'nunc': str}):
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
                    calidad_vinculado=str(row.get('calidad_vinculado', '')).strip(),
                    estado=str(row.get('estado', '')).strip(),
                    etapa=str(row.get('etapa', '')).strip()
                )
                registros.append(registro)
                # Intentar guardar el registro
            
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
                rud = row.get('rud', 0)
                rud_desaparecido = row.get('1.0', 0)
                rud_vivo = row.get('2.0', 0)
                rud_muerto = row.get('3.0', 0)
                funcionario = row.get('funcionario', 0)
                
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
                    
                if not pd.isna(rud):
                    rud = int(rud) == 1
                else:
                    rud = False
                
                if not pd.isna(rud_desaparecido):
                    rud_desaparecido = int(rud_desaparecido) == 1
                else:
                    rud_desaparecido = False
                    
                if not pd.isna(rud_vivo):
                    rud_vivo = int(rud_vivo) == 1
                else:
                    rud_vivo = False
                    
                if not pd.isna(rud_muerto): 
                    rud_muerto = int(rud_muerto) == 1
                else:
                    rud_muerto = False
                    
                if not pd.isna(funcionario): 
                    funcionario = int(funcionario) == 1
                else:
                    funcionario = False
                
                registro = PersonasDf(
                    numero_identificacion=str(row.get('numero_documento', '')).strip(),
                    nombre_completo=str(row.get('nombre_completo', '')).strip(),
                    desaparcion_forzada=desaparicion,
                    homicidio=homicidio,
                    secuestro=secuestro,
                    reclutamiento_ilicito=reclutamiento,
                    rud=rud,
                    rud_desaparecido=rud_desaparecido,
                    rud_vivo=rud_vivo,
                    rud_muerto=rud_muerto,
                    funcionario_FGN=funcionario
                )
                registros.append(registro)
            
            # Insertar en bulk (mucho más eficiente que uno por uno)
            # El parámetro ignore_conflicts evita errores por duplicados
            PersonasDf.objects.bulk_create(registros, ignore_conflicts=True)
            counter += len(registros)
            
        return counter
    else:
        raise ValueError(f"Formato de archivo no soportado: {extension}")

@transaction.atomic
def cargar_rud(ruta_archivo):
    """
    Carga datos desde un archivo CSV al modelo RegistroUnicoDesaparecidos
    
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
                registro = RegistroUnicoDesaparecidos(
                    numero_radicado=str(row.get('numero_radicado', '')).strip(),
                    nombre_completo=str(row.get('nombre_completo', '')).strip(),
                    tipo_documento=str(row.get('tipo_documento', '')).strip(),
                    numero_documento=str(row.get('numero_documento', '')).strip(),
                    departamento_desaparicion=str(row.get('departamento_desaparicion', '')).strip(),
                    municipio_desaparicion=str(row.get('municipio_desaparicion', '')).strip(),
                    barrio_vereda_desaparicion=str(row.get('barrio/vereda_desaparicion', '')).strip(),
                    fecha_desaparicion=parse_date(row.get('fecha_desaparicion')),
                    sexo=str(row.get('sexo', '')).strip(),
                    edad_1=row.get('edad_1') if not pd.isna(row.get('edad_1')) else None,
                    edad_2=row.get('edad_2') if not pd.isna(row.get('edad_2')) else None,
                    estatura_1=row.get('estatura_1') if not pd.isna(row.get('estatura_1')) else None,
                    estatura_2=row.get('estatura_2') if not pd.isna(row.get('estatura_2')) else None,
                    ancestro_racial=str(row.get('ancestro_racial', '')).strip(),
                    estado_desaparicion=str(row.get('estado_desaparicion', '')).strip(),
                    senales_particulares=str(row.get('senales_particulares', '')).strip()
                )
                registros.append(registro)
            
            # Insertar en bulk (mucho más eficiente que uno por uno)
            # El parámetro ignore_conflicts evita errores por duplicados
            RegistroUnicoDesaparecidos.objects.bulk_create(registros, ignore_conflicts=True)
            counter += len(registros)
            
        return counter
    else:
        raise ValueError(f"Formato de archivo no soportado: {extension}")


@transaction.atomic
def cargar_perfiles_personas(ruta_archivo):
    """
    Carga perfiles de personas desde un archivo JSON al modelo PerfilPersona
    
    Args:
        ruta_archivo: Ruta al archivo JSON que contiene los perfiles
        
    Returns:
        int: Número de perfiles cargados
    """
    # Verificar que el archivo existe
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo {ruta_archivo} no existe")
    
    # Verificar la extensión del archivo
    _, extension = os.path.splitext(ruta_archivo)
    
    if extension.lower() != '.json':
        raise ValueError(f"El archivo debe ser .json, no {extension}")
    
    # Leer archivo JSON
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        perfiles_data = json.load(file)
    
    # Lista para almacenar los perfiles a crear
    perfiles = []
    counter = 0
    
    # Procesar cada perfil en el JSON
    for documento, datos in perfiles_data.items():
        try:
            perfil = PerfilPersona(
                documento=documento,
                nombre=datos.get('nombre', ''),
                total_casos=datos.get('total_casos', 0),
                perfil=datos.get('perfil', ''),
                error=datos.get('error', None),
                tiempo_generacion=datos.get('tiempo_generacion', None)
            )
            perfiles.append(perfil)
        except Exception as e:
            print(f"Error al procesar perfil {documento}: {str(e)}")
            continue
    
    # Insertar en bulk (mucho más eficiente que uno por uno)
    # El parámetro ignore_conflicts evita errores por duplicados
    PerfilPersona.objects.bulk_create(perfiles, ignore_conflicts=True)
    counter = len(perfiles)
            
    return counter


@transaction.atomic
def cargar_aparecidos_vivos_no_registrados(ruta_archivo):
    """
    Carga datos desde un archivo CSV al modelo AparecidosVivosNoRegistrados
    
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
                registro = AparecidosVivosNoRegistrados(
                    numeroRadicado=str(row.get('numeroRadicado', '')).strip(),
                    entidadradica=str(row.get('entidadradica', '')).strip(),
                    nombreRegional=str(row.get('nombreRegional', '')).strip(),
                    nombreSeccional=str(row.get('nombreSeccional', '')).strip(),
                    nombreUnidadBasica=str(row.get('nombreUnidadBasica', '')).strip(),
                    usuarioRegistra=str(row.get('usuarioRegistra', '')).strip(),
                    fechaDesaparicion=parse_date(row.get('fechaDesaparicion')),
                    desaparecido=str(row.get('desaparecido', '')).strip(),
                    nombreDocumento=str(row.get('nombreDocumento', '')).strip(),
                    numero=str(row.get('numero_documento', '')).strip(),
                    paisDesaparicion=str(row.get('paisDesaparicion', '')).strip(),
                    departamentoDesaparicion=str(row.get('departamentoDesaparicion', '')).strip(),
                    municipioDesaparicion=str(row.get('municipioDesaparicion', '')).strip(),
                    aportanteDatosDesaparecido=str(row.get('aportanteDatosDesaparecido', '')).strip(),
                    paisAportanteDatos=str(row.get('paisAportanteDatos', '')).strip(),
                    departamentoAportanteDatos=str(row.get('departamentoAportanteDatos', '')).strip(),
                    municipioAportanteDatos=str(row.get('municipioAportanteDatos', '')).strip(),
                    detalleDireccionAportanteDatos=str(row.get('detalleDireccionAportanteDatos', '')),
                    aportanteDatos=str(row.get('aportanteDatos', '')).strip()
                )
                registros.append(registro)
            
            # Insertar en bulk (mucho más eficiente que uno por uno)
            # El parámetro ignore_conflicts evita errores por duplicados
            AparecidosVivosNoRegistrados.objects.bulk_create(registros, ignore_conflicts=True)
            counter += len(registros)
            
        return counter
    else:
        raise ValueError(f"Formato de archivo no soportado: {extension}")
    
@transaction.atomic
def cargar_funcionarios(ruta_archivo):
    """
    Carga datos de funcionarios desde un archivo CSV al modelo Funcionario
    
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
                registro = Funcionario(
                    numero_documento=str(row.get('numero_documento', '')).strip(),
                    nombres_apellidos=str(row.get('nombres_apellidos', '')).strip(),
                    nom_cargo=str(row.get('nom_cargo', '')).strip(),
                    seccional=str(row.get('seccional', '')).strip(),
                    nom_dependencia=str(row.get('nom_dependencia', '')).strip(),
                    estado=str(row.get('estado', '')).strip(),
                    fuente=str(row.get('fuente', '')).strip()
                )
                registros.append(registro)
            
            # Insertar en bulk (mucho más eficiente que uno por uno)
            # El parámetro ignore_conflicts evita errores por duplicados
            Funcionario.objects.bulk_create(registros, ignore_conflicts=True)
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