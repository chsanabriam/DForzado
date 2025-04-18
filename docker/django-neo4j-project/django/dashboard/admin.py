from django.contrib import admin
from .models import ConsolidadoSpoa, PersonasDf

# Register your models here.

@admin.register(ConsolidadoSpoa)
class ConsolidadoSpoaAdmin(admin.ModelAdmin):
    list_display = ('nunc', 'delito', 'fecha_hechos', 'fecha_denuncia','unidad', 'fuente', 'calidad_vinculado')
    list_filter = ('fuente', 'seccional', 'unidad', 'grupo_delito')
    search_fields = ('nunc', 'nombre_completo', 'delito', 'relato')
    date_hierarchy = 'fecha_hechos'
    list_per_page = 20

@admin.register(PersonasDf)
class PersonasDfAdmin(admin.ModelAdmin):
    list_display = ('numero_identificacion', 'nombre_completo', 'desaparcion_forzada','homicidio', 'secuestro', 'reclutamiento_ilicito')
    list_filter = ('desaparcion_forzada', 'homicidio', 'secuestro', 'reclutamiento_ilicito')
    search_fields = ('numero_identificacion', 'nombre_completo')
    list_per_page = 20