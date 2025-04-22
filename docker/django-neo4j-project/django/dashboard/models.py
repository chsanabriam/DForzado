from django.db import models

# Create your models here

class ConsolidadoSpoa(models.Model):
    """
    Modelo para almacenar los datos consolidados del SPOA
    """
    nunc = models.CharField(max_length=100, primary_key=True)
    fecha_hechos = models.DateField(null=True, blank=True)
    fecha_denuncia = models.DateField(null=True, blank=True)
    seccional = models.CharField(max_length=100, null=True, blank=True)
    unidad = models.CharField(max_length=100, null=True, blank=True)
    despacho = models.CharField(max_length=200, null=True, blank=True)
    numero_documento = models.CharField(max_length=50, null=True, blank=True)
    nombre_completo = models.CharField(max_length=200, null=True, blank=True)
    relato = models.TextField(null=True, blank=True)
    delito = models.CharField(max_length=200, null=True, blank=True)
    grupo_delito = models.CharField(max_length=200, null=True, blank=True)
    necropsia = models.CharField(max_length=100, null=True, blank=True)
    fuente = models.CharField(max_length=100, null=True, blank=True)
    calidad_vinculado = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        verbose_name = "Consolidado SPOA"
        verbose_name_plural = "Consolidados SPOA"
        
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
    
    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        
    def __str__(self):
        return self.nombre_completo


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
    estado_desaparicion = models.CharField(max_length=100, null=True, blank=True)
    senales_particulares = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Registro Unico de Desaparecidos"
        verbose_name_plural = "Registros Unicos de Desaparecidos"
        
    def __str__(self):
        return f"{self.numero_radicado} - {self.nombre_completo}"