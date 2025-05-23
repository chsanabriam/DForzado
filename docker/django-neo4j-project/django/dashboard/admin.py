from django.contrib import admin
from .models import (
    ConsolidadoSpoa,
    PersonasDf,
    RegistroUnicoDesaparecidos,
    PerfilPersona,
    AparecidosVivosNoRegistrados,
    Funcionario
)

# Register your models here.

@admin.register(ConsolidadoSpoa)
class ConsolidadoSpoaAdmin(admin.ModelAdmin):
    list_display = ('nunc', 'delito', 'fecha_hechos', 'fecha_denuncia','unidad', 'fuente', 'etapa', 'estado')
    list_filter = ('fuente', 'seccional', 'unidad', 'grupo_delito')
    search_fields = ('nunc', 'nombre_completo', 'delito', 'relato', 'numero_documento')
    date_hierarchy = 'fecha_hechos'
    list_per_page = 20

@admin.register(PersonasDf)
class PersonasDfAdmin(admin.ModelAdmin):
    list_display = ('numero_identificacion', 'nombre_completo', 'desaparcion_forzada','homicidio', 'secuestro', 'reclutamiento_ilicito', 'rud')
    list_filter = ('desaparcion_forzada', 'homicidio', 'secuestro', 'reclutamiento_ilicito', 'rud')
    search_fields = ('numero_identificacion', 'nombre_completo')
    list_per_page = 20
    
@admin.register(RegistroUnicoDesaparecidos)
class RegistroUnicoDesaparecidosAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'nombre_completo', 'numero_radicado', 'fecha_desaparicion', 'estado_desaparicion')
    list_filter = ('numero_documento', 'nombre_completo', 'numero_radicado', 'fecha_desaparicion', 'estado_desaparicion')
    search_fields = ('numero_documento', 'nombre_completo', 'numero_radicado')
    list_per_page = 20
    
@admin.register(PerfilPersona)
class PerfilPersonaAdmin(admin.ModelAdmin):
    list_display = ('documento', 'nombre', 'total_casos', 'fecha_creacion', 'fecha_actualizacion')
    search_fields = ('documento', 'nombre')
    list_filter = ('fecha_creacion', 'fecha_actualizacion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    list_per_page = 20

@admin.register(AparecidosVivosNoRegistrados)
class AparecidosVivosNoRegistradosAdmin(admin.ModelAdmin):
    list_display = ('numeroRadicado', 'desaparecido', 'numero', 'fechaDesaparicion', 'departamentoDesaparicion', 'municipioDesaparicion')
    list_filter = ('fechaDesaparicion', 'departamentoDesaparicion', 'municipioDesaparicion', 'nombreRegional', 'nombreSeccional')
    search_fields = ('numeroRadicado', 'desaparecido', 'numero', 'usuarioRegistra')
    date_hierarchy = 'fechaDesaparicion'
    list_per_page = 20
    
@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'nombres_apellidos', 'nom_cargo', 'seccional', 'nom_dependencia', 'estado')
    list_filter = ('estado', 'seccional', 'nom_cargo', 'fuente')
    search_fields = ('numero_documento', 'nombres_apellidos', 'nom_cargo', 'nom_dependencia')
    list_per_page = 20
    date_hierarchy = 'fecha_registro'