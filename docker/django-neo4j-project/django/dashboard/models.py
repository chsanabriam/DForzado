from django.db import models

# Create your models here

class ConsolidadoSpoa(models.Model):
    """
    Modelo para almacenar los datos consolidados del SPOA
    """
    # Campos que comúnmente causan problemas de longitud - AUMENTADOS
    nunc = models.CharField(max_length=200)  # Aumentado de 100 a 200
    fecha_hechos = models.DateField(null=True, blank=True)
    fecha_denuncia = models.DateField(null=True, blank=True)
    seccional = models.CharField(max_length=200, null=True, blank=True)  # Aumentado de 100 a 200
    unidad = models.CharField(max_length=300, null=True, blank=True)  # Aumentado de 100 a 300
    despacho = models.CharField(max_length=500, null=True, blank=True)  # Aumentado de 200 a 500
    numero_documento = models.CharField(max_length=100, null=True, blank=True)  # Aumentado de 50 a 100
    nombre_completo = models.CharField(max_length=300, null=True, blank=True)  # Aumentado de 200 a 300
    relato = models.TextField(null=True, blank=True)  # TextField no tiene límite
    delito = models.CharField(max_length=500, null=True, blank=True)  # Aumentado de 200 a 500
    grupo_delito = models.CharField(max_length=300, null=True, blank=True)  # Aumentado de 200 a 300
    necropsia = models.CharField(max_length=200, null=True, blank=True)  # Aumentado de 100 a 200
    fuente = models.CharField(max_length=200, null=True, blank=True)  # Aumentado de 100 a 200
    calidad_vinculado = models.CharField(max_length=200, null=True, blank=True)  # Aumentado de 100 a 200
    etapa = models.CharField(max_length=200, null=True, blank=True)  # Aumentado de 100 a 200
    estado = models.CharField(max_length=200, null=True, blank=True)  # Aumentado de 100 a 200
    
    class Meta:
        verbose_name = "Consolidado SPOA"
        verbose_name_plural = "Consolidados SPOA"
        # Definir clave primaria compuesta
        # unique_together = ('nunc', 'numero_documento', 'delito')
        # Índices para mejorar el rendimiento
        indexes = [
            models.Index(fields=['nunc']),
            models.Index(fields=['numero_documento']),
            models.Index(fields=['fecha_hechos']),
            models.Index(fields=['seccional']),
            models.Index(fields=['unidad']),
        ]
        
    def __str__(self):
        return f"{self.nunc} - {self.delito}"


class PersonasDf(models.Model):
    """
    Modelo para almacenar información de personas y sus relaciones con delitos
    """
    numero_identificacion = models.CharField(max_length=50, primary_key=True)
    nombre_completo = models.CharField(max_length=200)
    desaparcion_forzada = models.BooleanField(default=False)
    homicidio = models.BooleanField(default=False)
    secuestro = models.BooleanField(default=False)
    reclutamiento_ilicito = models.BooleanField(default=False)
    rud = models.BooleanField(default=False)  # Nuevo campo para relacionar con Registro Unido de Desaparecidos
    
    # Nuevos campos para el estado de desaparición
    rud_desaparecido = models.BooleanField(default=False)  # 1.0
    rud_vivo = models.BooleanField(default=False)          # 2.0
    rud_muerto = models.BooleanField(default=False)        # 3.0
    funcionario_FGN = models.BooleanField(default=False)  # Nuevo campo para relacionar si la persona es funcionario de la FGN.
    
    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        
    def __str__(self):
        return self.nombre_completo

class Funcionario(models.Model):
    """
    Modelo para almacenar información de funcionarios
    """
    numero_documento = models.CharField(max_length=50, primary_key=True)
    nombres_apellidos = models.CharField(max_length=200)
    nom_cargo = models.CharField(max_length=100, null=True, blank=True)
    seccional = models.CharField(max_length=100, null=True, blank=True)
    nom_dependencia = models.CharField(max_length=200, null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)
    fuente = models.CharField(max_length=100, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Funcionario"
        verbose_name_plural = "Funcionarios"
        
    def __str__(self):
        return f"{self.nombres_apellidos} ({self.numero_documento})"

class RegistroUnicoDesaparecidos(models.Model):
    """
    Modelo para almacenar información del Registro Unido de Desaparecidos (RUD)
    """
    numero_radicado = models.CharField(max_length=100, primary_key=True)
    nombre_completo = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=50, null=True, blank=True)
    numero_documento = models.CharField(max_length=50, null=True, blank=True)
    departamento_desaparicion = models.CharField(max_length=100, null=True, blank=True)
    municipio_desaparicion = models.CharField(max_length=100, null=True, blank=True)
    barrio_vereda_desaparicion = models.CharField(max_length=200, null=True, blank=True)
    fecha_desaparicion = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=20, null=True, blank=True)
    edad_1 = models.IntegerField(null=True, blank=True)
    edad_2 = models.IntegerField(null=True, blank=True)
    estatura_1 = models.FloatField(null=True, blank=True)
    estatura_2 = models.FloatField(null=True, blank=True)
    ancestro_racial = models.CharField(max_length=100, null=True, blank=True)
    estado_desaparicion = models.CharField(max_length=100, null=True, blank=True, choices=[
        ("1.0", "Desaparecido"),
        ("2.0", "Vivo"),
        ("3.0", "Muerto"),
    ])
    senales_particulares = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Registro Unico de Desaparecidos"
        verbose_name_plural = "Registros Unicos de Desaparecidos"
        
    def __str__(self):
        return f"{self.numero_radicado} - {self.nombre_completo}"
    
    
class PerfilPersona(models.Model):
    """
    Modelo para almacenar perfiles de personas generados con información consolidada
    """
    documento = models.CharField(max_length=50, primary_key=True)
    nombre = models.CharField(max_length=200)
    total_casos = models.IntegerField(default=0)
    perfil = models.TextField()
    error = models.TextField(null=True, blank=True)
    tiempo_generacion = models.FloatField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Persona"
        verbose_name_plural = "Perfiles de Personas"
        
    def __str__(self):
        return f"{self.nombre} ({self.documento})"
    

class AparecidosVivosNoRegistrados(models.Model):
    """
    Modelo para almacenar información de personas aparecidas vivas no registradas
    """
    numeroRadicado = models.CharField(max_length=100, primary_key=True)
    entidadradica = models.CharField(max_length=100, null=True, blank=True)
    nombreRegional = models.CharField(max_length=100, null=True, blank=True)
    nombreSeccional = models.CharField(max_length=100, null=True, blank=True)
    nombreUnidadBasica = models.CharField(max_length=200, null=True, blank=True)
    usuarioRegistra = models.CharField(max_length=100, null=True, blank=True)
    fechaDesaparicion = models.DateField(null=True, blank=True)
    desaparecido = models.CharField(max_length=200, null=True, blank=True)
    nombreDocumento = models.CharField(max_length=50, null=True, blank=True)
    numero = models.CharField(max_length=50, null=True, blank=True)
    paisDesaparicion = models.CharField(max_length=100, null=True, blank=True)
    departamentoDesaparicion = models.CharField(max_length=100, null=True, blank=True)
    municipioDesaparicion = models.CharField(max_length=100, null=True, blank=True)
    aportanteDatosDesaparecido = models.CharField(max_length=200, null=True, blank=True)
    paisAportanteDatos = models.CharField(max_length=100, null=True, blank=True)
    departamentoAportanteDatos = models.CharField(max_length=100, null=True, blank=True)
    municipioAportanteDatos = models.CharField(max_length=100, null=True, blank=True)
    detalleDireccionAportanteDatos = models.TextField(null=True, blank=True)
    aportanteDatos = models.CharField(max_length=200, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True) # Esta es para tener conocimiento de carga 
    
    class Meta:
        verbose_name = "Aparecido Vivo No Registrado"
        verbose_name_plural = "Aparecidos Vivos No Registrados"
        
    def __str__(self):
        return f"{self.numeroRadicado} - {self.desaparecido}"