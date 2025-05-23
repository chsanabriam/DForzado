from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import time
import markdown
import os
from xhtml2pdf import pisa



# Importar el nuevo modelo
from .models import (
    ConsolidadoSpoa,
    PersonasDf,
    RegistroUnicoDesaparecidos,
    PerfilPersona,
    AparecidosVivosNoRegistrados,
    Funcionario
)
from .utils import obtener_distribucion_por_fuente, obtener_distribucion_por_unidad

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del dashboard con datos generales
    """
    template_name = 'dashboard/pages/dashboard.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener totales
        context['total_spoa'] = ConsolidadoSpoa.objects.count()
        context['total_personas'] = PersonasDf.objects.count()
        
        # Obtener distribución por fuente
        fuentes = obtener_distribucion_por_fuente()
        context['fuentes_labels'] = json.dumps([f['fuente'] for f in fuentes])
        context['fuentes_data'] = json.dumps([f['cantidad'] for f in fuentes])
        
        # Obtener distribución por unidad
        unidades = obtener_distribucion_por_unidad()
        context['unidades_labels'] = json.dumps([u['unidad'] for u in unidades])
        context['unidades_data'] = json.dumps([u['cantidad'] for u in unidades])
        
        # Obtener distribución por seccional
        seccionales = list(ConsolidadoSpoa.objects.values('seccional')
                        .annotate(cantidad=Count('seccional'))
                        .filter(seccional__isnull=False)
                        .exclude(seccional='')
                        .order_by('-cantidad'))
        context['seccionales_data'] = json.dumps(seccionales)
        
        # Obtener distribución por necropsia
        necropsias = list(ConsolidadoSpoa.objects.values('necropsia')
                        .annotate(cantidad=Count('necropsia'))
                        .filter(necropsia__isnull=False)
                        .exclude(necropsia='')
                        .order_by('-cantidad'))
        context['necropsias_labels'] = json.dumps([n['necropsia'] for n in necropsias])
        context['necropsias_data'] = json.dumps([n['cantidad'] for n in necropsias])
        
        # Obtener conteo de delitos
        context['total_desaparicion'] = PersonasDf.objects.filter(desaparcion_forzada=True).count()
        context['total_homicidio'] = PersonasDf.objects.filter(homicidio=True).count()
        context['total_secuestro'] = PersonasDf.objects.filter(secuestro=True).count()
        context['total_reclutamiento'] = PersonasDf.objects.filter(reclutamiento_ilicito=True).count()
        context['total_rud'] = PersonasDf.objects.filter(rud=True).count()
        
        # Preparar datos para la intersección de delitos
        delitos_intersecciones = {
            'desaparcion_forzada': [
                {'delito': 'Homicidio', 'cantidad': PersonasDf.objects.filter(desaparcion_forzada=True, homicidio=True).count()},
                {'delito': 'Secuestro', 'cantidad': PersonasDf.objects.filter(desaparcion_forzada=True, secuestro=True).count()},
                {'delito': 'Reclutamiento', 'cantidad': PersonasDf.objects.filter(desaparcion_forzada=True, reclutamiento_ilicito=True).count()},
                {'delito': 'RUD', 'cantidad': PersonasDf.objects.filter(desaparcion_forzada=True, rud=True).count()}
            ],
            'homicidio': [
                {'delito': 'Desaparición Forzada', 'cantidad': PersonasDf.objects.filter(homicidio=True, desaparcion_forzada=True).count()},
                {'delito': 'Secuestro', 'cantidad': PersonasDf.objects.filter(homicidio=True, secuestro=True).count()},
                {'delito': 'Reclutamiento', 'cantidad': PersonasDf.objects.filter(homicidio=True, reclutamiento_ilicito=True).count()},
                {'delito': 'RUD', 'cantidad': PersonasDf.objects.filter(homicidio=True, rud=True).count()}
            ],
            'secuestro': [
                {'delito': 'Desaparición Forzada', 'cantidad': PersonasDf.objects.filter(secuestro=True, desaparcion_forzada=True).count()},
                {'delito': 'Homicidio', 'cantidad': PersonasDf.objects.filter(secuestro=True, homicidio=True).count()},
                {'delito': 'Reclutamiento', 'cantidad': PersonasDf.objects.filter(secuestro=True, reclutamiento_ilicito=True).count()},
                {'delito': 'RUD', 'cantidad': PersonasDf.objects.filter(secuestro=True, rud=True).count()}
            ],
            'reclutamiento_ilicito': [
                {'delito': 'Desaparición Forzada', 'cantidad': PersonasDf.objects.filter(reclutamiento_ilicito=True, desaparcion_forzada=True).count()},
                {'delito': 'Homicidio', 'cantidad': PersonasDf.objects.filter(reclutamiento_ilicito=True, homicidio=True).count()},
                {'delito': 'Secuestro', 'cantidad': PersonasDf.objects.filter(reclutamiento_ilicito=True, secuestro=True).count()},
                {'delito': 'RUD', 'cantidad': PersonasDf.objects.filter(reclutamiento_ilicito=True, rud=True).count()}
            ],
            'rud': [
                {'delito': 'Desaparición Forzada', 'cantidad': PersonasDf.objects.filter(rud=True, desaparcion_forzada=True).count()},
                {'delito': 'Homicidio', 'cantidad': PersonasDf.objects.filter(rud=True, homicidio=True).count()},
                {'delito': 'Secuestro', 'cantidad': PersonasDf.objects.filter(rud=True, secuestro=True).count()},
                {'delito': 'Reclutamiento', 'cantidad': PersonasDf.objects.filter(rud=True, reclutamiento_ilicito=True).count()}
            ]
        }
        context['delitos_intersecciones'] = json.dumps(delitos_intersecciones)
        
        return context


class DistribucionPorFuenteView(LoginRequiredMixin, TemplateView):
    """
    Vista para la distribución por fuente
    """
    template_name = 'dashboard/pages/distribucion_fuente.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_spoa'] = ConsolidadoSpoa.objects.count()
        fuentes = obtener_distribucion_por_fuente()
        context['fuentes'] = fuentes
        context['fuentes_labels'] = json.dumps([f['fuente'] for f in fuentes])
        context['fuentes_data'] = json.dumps([f['cantidad'] for f in fuentes])
        
        return context


class DistribucionPorUnidadView(LoginRequiredMixin, TemplateView):
    """
    Vista para la distribución por unidad
    """
    template_name = 'dashboard/pages/distribucion_unidad.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_spoa'] = ConsolidadoSpoa.objects.count()
        unidades = obtener_distribucion_por_unidad()
        context['unidades'] = unidades
        context['unidades_labels'] = json.dumps([u['unidad'] for u in unidades])
        context['unidades_data'] = json.dumps([u['cantidad'] for u in unidades])
        
        return context


# API para el dashboard interactivo
class ApiRegistrosPorFuenteView(LoginRequiredMixin, View):
    """
    API para obtener registros filtrados por fuente
    """
    def get(self, request):
        fuente = request.GET.get('fuente', '')
        pagina = int(request.GET.get('pagina', 1))
        registros_por_pagina = 10
        
        if not fuente:
            return JsonResponse({'error': 'Parámetro fuente es requerido'}, status=400)
        
        # Obtener registros filtrados
        registros = ConsolidadoSpoa.objects.filter(fuente=fuente).order_by('-fecha_hechos')
        
        # Paginar resultados
        paginator = Paginator(registros, registros_por_pagina)
        registros_pagina = paginator.get_page(pagina)
        
        # Formatear resultados
        resultados = []
        for registro in registros_pagina:
            resultados.append({
                'nunc': registro.nunc,
                'fecha_hechos': registro.fecha_hechos.strftime('%Y-%m-%d') if registro.fecha_hechos else None,
                'nombre_completo': registro.nombre_completo,
                'delito': registro.delito,
                'unidad': registro.unidad
            })
        
        return JsonResponse({
            'registros': resultados,
            'total_registros': paginator.count,
            'total_paginas': paginator.num_pages,
            'pagina_actual': pagina
        })


class ApiRegistrosPorSeccionalView(LoginRequiredMixin, View):
    """
    API para obtener registros filtrados por seccional
    """
    def get(self, request):
        seccional = request.GET.get('seccional', '')
        pagina = int(request.GET.get('pagina', 1))
        registros_por_pagina = 10
        
        if not seccional:
            return JsonResponse({'error': 'Parámetro seccional es requerido'}, status=400)
        
        # Obtener registros filtrados
        registros = ConsolidadoSpoa.objects.filter(seccional=seccional).order_by('-fecha_hechos')
        
        # Paginar resultados
        paginator = Paginator(registros, registros_por_pagina)
        registros_pagina = paginator.get_page(pagina)
        
        # Formatear resultados
        resultados = []
        for registro in registros_pagina:
            resultados.append({
                'nunc': registro.nunc,
                'unidad': registro.unidad,
                'despacho': registro.despacho,
                'delito': registro.delito,
                'fecha_hechos': registro.fecha_hechos.strftime('%Y-%m-%d') if registro.fecha_hechos else None
            })
        
        return JsonResponse({
            'registros': resultados,
            'total_registros': paginator.count,
            'total_paginas': paginator.num_pages,
            'pagina_actual': pagina
        })


class ApiUnidadesPorSeccionalView(LoginRequiredMixin, View):
    """
    API para obtener unidades filtradas por seccional
    """
    def get(self, request):
        seccional = request.GET.get('seccional', '')
        
        if not seccional:
            return JsonResponse({'error': 'Parámetro seccional es requerido'}, status=400)
        
        # Obtener unidades filtradas
        unidades = (ConsolidadoSpoa.objects.filter(seccional=seccional)
                    .values('unidad')
                    .annotate(cantidad=Count('unidad'))
                    .filter(unidad__isnull=False)
                    .exclude(unidad='')
                    .order_by('-cantidad'))
        
        return JsonResponse(list(unidades), safe=False)


class ApiDespachosPorSeccionalView(LoginRequiredMixin, View):
    """
    API para obtener despachos filtrados por seccional
    """
    def get(self, request):
        seccional = request.GET.get('seccional', '')
        
        if not seccional:
            return JsonResponse({'error': 'Parámetro seccional es requerido'}, status=400)
        
        # Obtener despachos filtrados
        despachos = (ConsolidadoSpoa.objects.filter(seccional=seccional)
                    .values('despacho')
                    .annotate(cantidad=Count('despacho'))
                    .filter(despacho__isnull=False)
                    .exclude(despacho='')
                    .order_by('-cantidad'))
        
        return JsonResponse(list(despachos), safe=False)


class ApiRegistrosPorNecropsiaView(LoginRequiredMixin, View):
    """
    API para obtener registros filtrados por necropsia
    """
    def get(self, request):
        necropsia = request.GET.get('necropsia', '')
        pagina = int(request.GET.get('pagina', 1))
        registros_por_pagina = 10
        
        if not necropsia:
            return JsonResponse({'error': 'Parámetro necropsia es requerido'}, status=400)
        
        # Obtener registros filtrados
        registros = ConsolidadoSpoa.objects.filter(necropsia=necropsia).order_by('-fecha_hechos')
        
        # Paginar resultados
        paginator = Paginator(registros, registros_por_pagina)
        registros_pagina = paginator.get_page(pagina)
        
        # Formatear resultados
        resultados = []
        for registro in registros_pagina:
            resultados.append({
                'nunc': registro.nunc,
                'fecha_hechos': registro.fecha_hechos.strftime('%Y-%m-%d') if registro.fecha_hechos else None,
                'nombre_completo': registro.nombre_completo,
                'delito': registro.delito,
                'fuente': registro.fuente
            })
        
        return JsonResponse({
            'registros': resultados,
            'total_registros': paginator.count,
            'total_paginas': paginator.num_pages,
            'pagina_actual': pagina
        })


class ApiDetalleRegistroView(LoginRequiredMixin, View):
    """
    API para obtener el detalle de un registro específico
    """
    def get(self, request):
        nunc = request.GET.get('nunc', '')
        
        if not nunc:
            return JsonResponse({'error': 'Parámetro nunc es requerido'}, status=400)
        
        try:
            registro = ConsolidadoSpoa.objects.get(nunc=nunc)
            
            detalle = {
                'nunc': registro.nunc,
                'fecha_hechos': registro.fecha_hechos.strftime('%Y-%m-%d') if registro.fecha_hechos else None,
                'fecha_denuncia': registro.fecha_denuncia.strftime('%Y-%m-%d') if registro.fecha_denuncia else None,
                'seccional': registro.seccional,
                'unidad': registro.unidad,
                'despacho': registro.despacho,
                'numero_documento': registro.numero_documento,
                'nombre_completo': registro.nombre_completo,
                'relato': registro.relato,
                'delito': registro.delito,
                'grupo_delito': registro.grupo_delito,
                'necropsia': registro.necropsia,
                'fuente': registro.fuente,
                'calidad_vinculado': registro.calidad_vinculado,
                'estado': registro.estado,
                'etapa': registro.etapa
            }
            
            return JsonResponse(detalle)
        except ConsolidadoSpoa.DoesNotExist:
            return JsonResponse({'error': 'Registro no encontrado'}, status=404)


class ApiInterseccionesDelitoView(LoginRequiredMixin, View):
    """
    API para obtener las intersecciones de un delito con otros
    """
    def get(self, request):
        delito = request.GET.get('delito', '')
        
        if not delito or delito not in ['desaparcion_forzada', 'homicidio', 'secuestro', 'reclutamiento_ilicito', 'rud']:
            return JsonResponse({'error': 'Parámetro delito no válido'}, status=400)
        
        # Definir las consultas basadas en el delito seleccionado
        intersecciones = []
        
        if delito == 'desaparcion_forzada':
            intersecciones = [
                {'delito': 'Homicidio', 'cantidad': PersonasDf.objects.filter(desaparcion_forzada=True, homicidio=True).count()},
                {'delito': 'Secuestro', 'cantidad': PersonasDf.objects.filter(desaparcion_forzada=True, secuestro=True).count()},
                {'delito': 'Reclutamiento', 'cantidad': PersonasDf.objects.filter(desaparcion_forzada=True, reclutamiento_ilicito=True).count()},
                {'delito': 'RUD', 'cantidad': PersonasDf.objects.filter(desaparcion_forzada=True, rud=True).count()}
            ]
        elif delito == 'homicidio':
            intersecciones = [
                {'delito': 'Desaparición Forzada', 'cantidad': PersonasDf.objects.filter(homicidio=True, desaparcion_forzada=True).count()},
                {'delito': 'Secuestro', 'cantidad': PersonasDf.objects.filter(homicidio=True, secuestro=True).count()},
                {'delito': 'Reclutamiento', 'cantidad': PersonasDf.objects.filter(homicidio=True, reclutamiento_ilicito=True).count()},
                {'delito': 'RUD', 'cantidad': PersonasDf.objects.filter(homicidio=True, rud=True).count()}
            ]
        elif delito == 'secuestro':
            intersecciones = [
                {'delito': 'Desaparición Forzada', 'cantidad': PersonasDf.objects.filter(secuestro=True, desaparcion_forzada=True).count()},
                {'delito': 'Homicidio', 'cantidad': PersonasDf.objects.filter(secuestro=True, homicidio=True).count()},
                {'delito': 'Reclutamiento', 'cantidad': PersonasDf.objects.filter(secuestro=True, reclutamiento_ilicito=True).count()},
                {'delito': 'RUD', 'cantidad': PersonasDf.objects.filter(secuestro=True, rud=True).count()}
            ]
        elif delito == 'reclutamiento_ilicito':
            intersecciones = [
                {'delito': 'Desaparición Forzada', 'cantidad': PersonasDf.objects.filter(reclutamiento_ilicito=True, desaparcion_forzada=True).count()},
                {'delito': 'Homicidio', 'cantidad': PersonasDf.objects.filter(reclutamiento_ilicito=True, homicidio=True).count()},
                {'delito': 'Secuestro', 'cantidad': PersonasDf.objects.filter(reclutamiento_ilicito=True, secuestro=True).count()},
                {'delito': 'RUD', 'cantidad': PersonasDf.objects.filter(reclutamiento_ilicito=True, rud=True).count()}
            ]
        elif delito == 'rud':
            intersecciones = [
                {'delito': 'Desaparición Forzada', 'cantidad': PersonasDf.objects.filter(rud=True, desaparcion_forzada=True).count()},
                {'delito': 'Homicidio', 'cantidad': PersonasDf.objects.filter(rud=True, homicidio=True).count()},
                {'delito': 'Secuestro', 'cantidad': PersonasDf.objects.filter(rud=True, secuestro=True).count()},
                {'delito': 'Reclutamiento', 'cantidad': PersonasDf.objects.filter(rud=True, reclutamiento_ilicito=True).count()}
            ]
        
        return JsonResponse({
            'delito': delito,
            'intersecciones': intersecciones
        })


class ApiDashboardDataView(LoginRequiredMixin, View):
    """
    API para obtener todos los datos del dashboard en un solo request
    Útil para actualizaciones en tiempo real
    """
    def get(self, request):
        # Obtener totales
        total_spoa = ConsolidadoSpoa.objects.count()
        total_personas = PersonasDf.objects.count()
        
        # Obtener distribución por fuente
        fuentes = obtener_distribucion_por_fuente()
        fuentes_labels = [f['fuente'] for f in fuentes]
        fuentes_data = [f['cantidad'] for f in fuentes]
        
        # Obtener distribución por unidad
        unidades = obtener_distribucion_por_unidad()
        unidades_labels = [u['unidad'] for u in unidades]
        unidades_data = [u['cantidad'] for u in unidades]
        
        # Obtener distribución por seccional
        seccionales = list(ConsolidadoSpoa.objects.values('seccional')
                        .annotate(cantidad=Count('seccional'))
                        .filter(seccional__isnull=False)
                        .exclude(seccional='')
                        .order_by('-cantidad'))
        
        # Obtener distribución por necropsia
        necropsias = list(ConsolidadoSpoa.objects.values('necropsia')
                        .annotate(cantidad=Count('necropsia'))
                        .filter(necropsia__isnull=False)
                        .exclude(necropsia='')
                        .order_by('-cantidad'))
        necropsias_labels = [n['necropsia'] for n in necropsias]
        necropsias_data = [n['cantidad'] for n in necropsias]
        
        # Obtener conteo de delitos
        total_desaparicion = PersonasDf.objects.filter(desaparcion_forzada=True).count()
        total_homicidio = PersonasDf.objects.filter(homicidio=True).count()
        total_secuestro = PersonasDf.objects.filter(secuestro=True).count()
        total_reclutamiento = PersonasDf.objects.filter(reclutamiento_ilicito=True).count()
        total_rud = PersonasDf.objects.filter(rud=True).count()
        
        return JsonResponse({
            'totalSpoa': total_spoa,
            'totalPersonas': total_personas,
            'fuentesLabels': fuentes_labels,
            'fuentesData': fuentes_data,
            'unidadesLabels': unidades_labels,
            'unidadesData': unidades_data,
            'seccionalesData': seccionales,
            'necropsiasLabels': necropsias_labels,
            'necropsiasData': necropsias_data,
            'totalDesaparicion': total_desaparicion,
            'totalHomicidio': total_homicidio,
            'totalSecuestro': total_secuestro,
            'totalReclutamiento': total_reclutamiento,
            'totalRUD': total_rud
        })


class ApiCheckUpdatesView(LoginRequiredMixin, View):
    """
    API para verificar si hay actualizaciones disponibles
    """
    def get(self, request):
        # En un entorno real, aquí verificarías si hay cambios en la base de datos
        # desde la última consulta, usando timestamps o alguna otra técnica
        
        # Para el ejemplo, simplemente devuelve falso
        return JsonResponse({'hasUpdates': False})

class PersonasView(LoginRequiredMixin, TemplateView):
    """
    Vista para la página de personas y sus delitos asociados
    """
    template_name = 'dashboard/pages/personas.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['total_personas'] = PersonasDf.objects.count()
        context['total_desaparicion'] = PersonasDf.objects.filter(desaparcion_forzada=True).count()
        context['total_homicidio'] = PersonasDf.objects.filter(homicidio=True).count()
        context['total_secuestro'] = PersonasDf.objects.filter(secuestro=True).count()
        context['total_reclutamiento'] = PersonasDf.objects.filter(reclutamiento_ilicito=True).count()
        context['total_rud'] = PersonasDf.objects.filter(rud=True).count()
        
        return context


class ApiPersonasFiltradas(LoginRequiredMixin, View):
    """
    API para obtener personas filtradas por dos modos:
    1. Búsqueda por texto (nombre/documento)
    2. Búsqueda por delitos (operador AND)
    """
    def get(self, request):
        # Parámetros de paginación
        pagina = int(request.GET.get('pagina', 1))
        
        # Numero de registros por página
        registros_por_pagina = int(request.GET.get('por_pagina', 10))
        
        # Modo de búsqueda (texto o delitos)
        modo_busqueda = request.GET.get('modo', 'texto')
        
        # Construir query base
        query = PersonasDf.objects.all()
        
        # Procesar según modo de búsqueda
        if modo_busqueda == 'texto':
            # Búsqueda por texto (nombre o documento)
            busqueda = request.GET.get('busqueda', '')
            
            if busqueda:
                query = query.filter(
                    Q(nombre_completo__icontains=busqueda) | 
                    Q(numero_identificacion__icontains=busqueda)
                )
        else:  # modo_busqueda == 'delitos'
            # Filtros de delitos usando operador AND
            filtro_desaparicion = request.GET.get('desaparicion', '')
            filtro_homicidio = request.GET.get('homicidio', '')
            filtro_secuestro = request.GET.get('secuestro', '')
            filtro_reclutamiento = request.GET.get('reclutamiento', '')
            filtro_rud_estado = request.GET.get('rud_estado', '')
            filtro_funcionario = request.GET.get('funcionario', '') 
            
            # Aplicar cada filtro como condición adicional (AND)
            if filtro_desaparicion.lower() == 'true':
                query = query.filter(desaparcion_forzada=True)
            elif filtro_desaparicion.lower() == 'false':
                query = query.filter(desaparcion_forzada=False)
                
            if filtro_homicidio.lower() == 'true':
                query = query.filter(homicidio=True)
            elif filtro_homicidio.lower() == 'false':
                query = query.filter(homicidio=False)
                
            if filtro_secuestro.lower() == 'true':
                query = query.filter(secuestro=True)
            elif filtro_secuestro.lower() == 'false':
                query = query.filter(secuestro=False)
                
            if filtro_reclutamiento.lower() == 'true':
                query = query.filter(reclutamiento_ilicito=True)
            elif filtro_reclutamiento.lower() == 'false':
                query = query.filter(reclutamiento_ilicito=False)
                
            # Nuevo filtro para funcionarios
            if filtro_funcionario.lower() == 'true':
                query = query.filter(funcionario_FGN=True)
            elif filtro_funcionario.lower() == 'false':
                query = query.filter(funcionario_FGN=False)
                
            # Filtro modificado para RUD con estados
            if filtro_rud_estado:
                if filtro_rud_estado == 'no_rud':
                    # No está en RUD
                    query = query.filter(rud=False)
                elif filtro_rud_estado == 'desaparecido':
                    # En RUD con estado 'Desaparecido' (1.0)
                    query = query.filter(
                        Q(rud=True) & 
                        Q(rud_desaparecido=True))
                    # Consulta adicional para obtener documentos con estado "Desaparecido"
                    documentos_desaparecidos = RegistroUnicoDesaparecidos.objects.filter(
                        estado_desaparicion="1.0"
                    ).values_list('numero_documento', flat=True)
                    query = query.filter(numero_identificacion__in=documentos_desaparecidos)
                elif filtro_rud_estado == 'vivo':
                    # En RUD con estado 'Vivo' (2.0)
                    query = query.filter(
                        Q(rud=True) & 
                        Q(rud_vivo=True))
                    documentos_vivos = RegistroUnicoDesaparecidos.objects.filter(
                        estado_desaparicion="2.0"
                    ).values_list('numero_documento', flat=True)
                    query = query.filter(numero_identificacion__in=documentos_vivos)
                elif filtro_rud_estado == 'muerto':
                    # En RUD con estado 'Muerto' (3.0)
                    query = query.filter(
                        Q(rud=True) & 
                        Q(rud_muerto=True))
                    documentos_muertos = RegistroUnicoDesaparecidos.objects.filter(
                        estado_desaparicion="3.0"
                    ).values_list('numero_documento', flat=True)
                    query = query.filter(numero_identificacion__in=documentos_muertos)
        
        # Ordenar resultados
        query = query.order_by('nombre_completo')
        
        # Contar total antes de paginar
        total_registros = query.count()
        
        # Paginar resultados
        paginator = Paginator(query, registros_por_pagina)
        personas_pagina = paginator.get_page(pagina)
        
        # Formatear resultados
        resultados = []
        for persona in personas_pagina:
            # Determinar el estado RUD
            rud_estado = None
            if persona.rud:
                # Buscar en el RUD para obtener el estado
                try:
                    # Buscar el registro más reciente (si hay múltiples)
                    rud_registro = RegistroUnicoDesaparecidos.objects.filter(
                        numero_documento=persona.numero_identificacion
                    ).order_by('-fecha_desaparicion').first()
                    
                    if rud_registro:
                        if rud_registro.estado_desaparicion == "1.0":
                            rud_estado = "desaparecido"
                        elif rud_registro.estado_desaparicion == "2.0":
                            rud_estado = "vivo"
                        elif rud_registro.estado_desaparicion == "3.0":
                            rud_estado = "muerto"
                except Exception as e:
                    print(f"Error al determinar estado RUD: {e}")
            
            resultados.append({
                'id': persona.numero_identificacion,
                'nombre': persona.nombre_completo,
                'desaparicion': persona.desaparcion_forzada,
                'homicidio': persona.homicidio,
                'secuestro': persona.secuestro,
                'reclutamiento': persona.reclutamiento_ilicito,
                'rud': persona.rud,
                'rud_estado': rud_estado,
                'funcionario': persona.funcionario_FGN
            })
        
        return JsonResponse({
            'personas': resultados,
            'total_registros': total_registros,
            'total_paginas': paginator.num_pages,
            'pagina_actual': pagina,
            'modo': modo_busqueda
        })


class ApiNoticiasCriminalesPorPersona(LoginRequiredMixin, View):
    """
    API para obtener noticias criminales asociadas a una persona
    """
    def get(self, request):
        numero_documento = request.GET.get('documento', '')
        delito = request.GET.get('delito', '')
        
        if not numero_documento:
            return JsonResponse({'error': 'Parámetro documento es requerido'}, status=400)
        
        # Para el caso de RUD, necesitamos consultar el modelo RegistroUnicoDesaparecidos
        if delito == 'rud':
            
            en_aparecidos_vivos = False
            try:
                # Aquí asumimos que hay un campo o condición que identifica a los aparecidos vivos no registrados
                # Por ejemplo, un estado_desaparicion "2.0" podría indicar "Vivo"
                aparecido_vivo = AparecidosVivosNoRegistrados.objects.filter(
                    numero=numero_documento
                ).exists()
                en_aparecidos_vivos = aparecido_vivo
            except Exception as e:
                print(f"Error al verificar aparecidos vivos: {e}")
            
            # Obtener datos del RUD para este documento
            try:
                # Intentar encontrar registro en el modelo RegistroUnicoDesaparecidos
                rud_registros = RegistroUnicoDesaparecidos.objects.filter(numero_documento=numero_documento)
                
                dict_estado = {
                    '1.0': 'Desaparecido',
                    '2.0': 'Vivo',
                    '3.0': 'Muerto',
                }
                
                # Formatear resultados
                resultados = []
                for rud in rud_registros:
                    resultados.append({
                        'nunc': rud.numero_radicado,  # Usar número de radicado como equivalente al NUNC
                        'fecha_hechos': rud.fecha_desaparicion.strftime('%Y-%m-%d') if rud.fecha_desaparicion else None,
                        'fecha_denuncia': None,  # RUD no tiene fecha de denuncia explícita
                        'delito': 'Desaparición',  # Asumimos que todos son del tipo desaparición
                        'unidad': 'Registro Único de Desaparecidos',
                        'departamento': rud.departamento_desaparicion,
                        'municipio': rud.municipio_desaparicion,
                        'barrio_vereda': rud.barrio_vereda_desaparicion,
                        'sexo': rud.sexo,
                        'edad': f"{rud.edad_1 or ''} - {rud.edad_2 or ''}",
                        'estatura': f"{rud.estatura_1 or ''} - {rud.estatura_2 or ''}",
                        'ancestro_racial': rud.ancestro_racial,
                        'estado_desaparicion': dict_estado[rud.estado_desaparicion],
                        'relato': f"Señales particulares: {rud.senales_particulares or 'No registradas'}",
                        'fuente': 'RUD'
                    })
                
                return JsonResponse({
                    'noticias': resultados,
                    'total': len(resultados),
                    'en_aparecidos_vivos': en_aparecidos_vivos
                })
                
            except Exception as e:
                return JsonResponse({
                    'error': f'Error al consultar RUD: {str(e)}',
                    'noticias': [],
                    'total': 0
                })
        else:
            # Base query para otros tipos de delitos
            noticias = ConsolidadoSpoa.objects.filter(numero_documento=numero_documento).order_by('-fecha_hechos')
            
            # Filtrar por delito específico si se proporciona
            if delito:
                if delito == 'desaparicion':
                    noticias = noticias.filter(grupo_delito__icontains='desaparicion')
                elif delito == 'homicidio':
                    noticias = noticias.filter(grupo_delito__icontains='homicidio')
                elif delito == 'secuestro':
                    noticias = noticias.filter(grupo_delito__icontains='secuestro')
                elif delito == 'reclutamiento':
                    noticias = noticias.filter(grupo_delito__icontains='reclut')
            
            # Formatear resultados
            resultados = []
            for noticia in noticias:
                resultados.append({
                    'nunc': noticia.nunc,
                    'fecha_hechos': noticia.fecha_hechos.strftime('%Y-%m-%d') if noticia.fecha_hechos else None,
                    'fecha_denuncia': noticia.fecha_denuncia.strftime('%Y-%m-%d') if noticia.fecha_denuncia else None,
                    'unidad': noticia.unidad,
                    'seccional': noticia.seccional,
                    'delito': noticia.delito,
                    'grupo_delito': noticia.grupo_delito,
                    'relato': noticia.relato,
                    'fuente': noticia.fuente,
                    'estado': noticia.estado,
                    'etapa': noticia.etapa
                })
            
            return JsonResponse({
                'noticias': resultados,
                'total': len(resultados)
            })


class ApiLineaTiempoPorPersona(LoginRequiredMixin, View):
    """
    API para obtener la línea de tiempo de noticias criminales de una persona
    """
    def get(self, request):
        numero_documento = request.GET.get('documento', '')
        
        if not numero_documento:
            return JsonResponse({'error': 'Parámetro documento es requerido'}, status=400)
        
        # Obtener todas las noticias ordenadas por fecha
        noticias = ConsolidadoSpoa.objects.filter(numero_documento=numero_documento)
        
        # Crear línea de tiempo combinando fechas de hechos y denuncias
        timeline = []
        
        for noticia in noticias:
            # Agregar fecha de hechos si existe
            if noticia.fecha_hechos:
                timeline.append({
                    'fecha': noticia.fecha_hechos.strftime('%Y-%m-%d'),
                    'tipo': 'hechos',
                    'nunc': noticia.nunc,
                    'delito': noticia.delito,
                    'grupo_delito': noticia.grupo_delito
                })
            
            # Agregar fecha de denuncia si existe
            if noticia.fecha_denuncia:
                timeline.append({
                    'fecha': noticia.fecha_denuncia.strftime('%Y-%m-%d'),
                    'tipo': 'denuncia',
                    'nunc': noticia.nunc,
                    'delito': noticia.delito,
                    'grupo_delito': noticia.grupo_delito
                })
        
        # Ordenar por fecha
        timeline_ordenado = sorted(timeline, key=lambda x: x['fecha'])
        
        return JsonResponse({
            'timeline': timeline_ordenado,
            'total': len(timeline_ordenado)
        })

class ApiFuncionarioView(LoginRequiredMixin, View):
    """
    API para obtener información básica de un funcionario por su documento
    """
    def get(self, request):
        documento = request.GET.get('documento', '')
        
        if not documento:
            return JsonResponse({'error': 'El parámetro documento es requerido'}, status=400)
        
        try:
            # Obtener información del funcionario
            funcionario = Funcionario.objects.get(numero_documento=documento)
            
            # Crear respuesta con solo la información básica del modelo Funcionario
            return JsonResponse({
                'numero_documento': funcionario.numero_documento,
                'nombres_apellidos': funcionario.nombres_apellidos,
                'nom_cargo': funcionario.nom_cargo,
                'seccional': funcionario.seccional,
                'nom_dependencia': funcionario.nom_dependencia,
                'estado': funcionario.estado,
                'fuente': funcionario.fuente,
                'fecha_registro': funcionario.fecha_registro.isoformat() if funcionario.fecha_registro else None
            })
            
        except Funcionario.DoesNotExist:
            return JsonResponse({
                'error': 'Funcionario no encontrado',
                'documento': documento
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'error': f'Error al obtener información del funcionario: {str(e)}',
                'documento': documento
            }, status=500)

# Añadir nueva vista API para perfiles
class ApiPerfilPersonaView(LoginRequiredMixin, View):
    """
    API para obtener el perfil de una persona
    """
    def get(self, request):
        documento = request.GET.get('documento', '')
        
        if not documento:
            return JsonResponse({'error': 'Parámetro documento es requerido'}, status=400)
        
        try:
            # Cargar el archivo JSON con los perfiles
            json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard', 'data', 'lote_completo_v2.json')
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    perfiles_json = json.load(f)
                
                # Verificar si el documento existe en el JSON
                if documento in perfiles_json:
                    # Obtener datos del perfil del JSON
                    perfil_data = perfiles_json[documento]
                    
                    # Determinar estado de delitos del texto del perfil
                    estados_delitos = self.extraer_estados_delitos(documento)
                    
                    # Crear respuesta
                    return JsonResponse({
                        'documento': perfil_data['documento'],
                        'nombre': perfil_data['nombre'],
                        'total_casos': perfil_data['total_casos'],
                        'perfil': perfil_data['perfil'],
                        'estados_delitos': estados_delitos,
                        'encontrado_en_json': True
                    })
            
            # Si no existe en el JSON o no se pudo cargar, obtener información básica
            try:
                # Obtener la persona
                persona = PersonasDf.objects.get(numero_identificacion=documento)
                
                # Contar noticias asociadas
                total_casos_spoa = ConsolidadoSpoa.objects.filter(numero_documento=documento).count()
                total_casos_rud = 0
                
                if persona.rud:
                    total_casos_rud = RegistroUnicoDesaparecidos.objects.filter(numero_documento=documento).count()
                
                total_casos = total_casos_spoa + total_casos_rud
                
                # Crear estados de delitos
                estados_delitos = {
                    'desaparicion': persona.desaparcion_forzada,
                    'homicidio': persona.homicidio,
                    'secuestro': persona.secuestro, 
                    'reclutamiento': persona.reclutamiento_ilicito,
                    'rud': persona.rud,
                    'funcionario': persona.funcionario_FGN
                }
                
                # Crear respuesta
                return JsonResponse({
                    'documento': documento,
                    'nombre': persona.nombre_completo,
                    'total_casos': total_casos,
                    'perfil': "Caracterización de la persona en construcción",
                    'estados_delitos': estados_delitos,
                    'encontrado_en_json': False
                })
                
            except PersonasDf.DoesNotExist:
                return JsonResponse({
                    'error': 'Persona no encontrada en la base de datos',
                    'documento': documento
                }, status=404)
        
        except Exception as e:
            return JsonResponse({
                'error': f'Error al obtener perfil: {str(e)}',
                'documento': documento
            }, status=500)
    
    def extraer_estados_delitos(self, documento):
        """
        Extrae el estado de los delitos a partir del documento de la persona
        """
        try:
            persona = PersonasDf.objects.get(numero_identificacion=documento)
        except PersonasDf.DoesNotExist:
            return JsonResponse({'error': 'Persona no encontrada'}, status=404)
        
        # Determinar estados basados en el contenido del perfil
        return {
            'desaparicion': persona.desaparcion_forzada,
            'homicidio': persona.homicidio,
            'secuestro':  persona.secuestro,
            'reclutamiento': persona.reclutamiento_ilicito,
            'rud': persona.rud,
            'funcionario': persona.funcionario_FGN
        }
    
    def buscar_terminos_delito(self, texto, terminos):
        """
        Busca términos relacionados con un delito en el texto del perfil
        """
        return any(termino in texto for termino in terminos)


@csrf_exempt
def exportar_perfil_pdf(request):
    """
    Vista para exportar el perfil a PDF
    """
    documento = request.GET.get('documento', '')
    
    if not documento:
        return JsonResponse({'error': 'Parámetro documento es requerido'}, status=400)
    
    try:
        # Cargar el archivo JSON con los perfiles
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard', 'data', 'lote_completo_v2.json')
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                perfiles_json = json.load(f)
            
            # Verificar si el documento existe en el JSON
            if documento in perfiles_json:
                perfil_data = perfiles_json[documento]
                
                # Convertir markdown a HTML
                html_content = markdown.markdown(perfil_data['perfil'])
                
                # Crear respuesta con PDF
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="perfil_{documento}.pdf"'
                
                # Plantilla HTML para el PDF
                html_template = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Reporte {perfil_data['nombre']}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1 {{ color: #003366; }}
                        h2, h3, h4 {{ color: #006699; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .content {{ line-height: 1.5; }}
                        .footer {{ margin-top: 30px; font-size: 0.8em; text-align: center; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>RESUMEN INTEGRAL - FISCALÍA GENERAL DE LA NACIÓN</h1>
                    </div>
                    <div class="content">
                        {html_content}
                    </div>
                    <div class="footer">
                        <p>Documento generado por el sistema de Nexus Crime de la Fiscalía General de la Nación</p>
                    </div>
                </body>
                </html>
                """
                
                # Generar PDF
                pisa_status = pisa.CreatePDF(html_template, dest=response)
                
                # Si hay error
                if pisa_status.err:
                    return JsonResponse({'error': 'Error al generar PDF'}, status=500)
                
                return response
            
        # Si no se encontró en el JSON, generar uno básico
        return JsonResponse({'error': 'Perfil no encontrado'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)


# # Añadir nueva vista API para perfiles
# class ApiPerfilPersonaView(LoginRequiredMixin, View):
#     """
#     API para obtener o generar el perfil completo de una persona
#     """
#     def get(self, request):
#         documento = request.GET.get('documento', '')
#         regenerar = request.GET.get('regenerar', 'false').lower() == 'true'
        
#         if not documento:
#             return JsonResponse({'error': 'Parámetro documento es requerido'}, status=400)
        
#         try:
#             # Intentar obtener perfil existente
#             perfil = None
#             if not regenerar:
#                 try:
#                     perfil = PerfilPersona.objects.get(documento=documento)
#                 except PerfilPersona.DoesNotExist:
#                     pass
            
#             # Si no existe o se solicita regenerar, crear nuevo perfil
#             if perfil is None:
#                 # Obtener datos de la persona
#                 try:
#                     persona = PersonasDf.objects.get(numero_identificacion=documento)
#                 except PersonasDf.DoesNotExist:
#                     return JsonResponse({'error': 'Persona no encontrada'}, status=404)
                
#                 # Obtener noticias criminales asociadas
#                 noticias_spoa = ConsolidadoSpoa.objects.filter(numero_documento=documento)
#                 noticias_rud = []
#                 if persona.rud:
#                     noticias_rud = RegistroUnicoDesaparecidos.objects.filter(numero_documento=documento)
                
#                 # Generar perfil
#                 start_time = time.time()
#                 perfil_contenido = self.generar_perfil(persona, noticias_spoa, noticias_rud)
#                 tiempo_generacion = time.time() - start_time
                
#                 # Guardar en la base de datos
#                 perfil = PerfilPersona(
#                     documento=documento,
#                     nombre=persona.nombre_completo,
#                     total_casos=noticias_spoa.count() + noticias_rud.count(),
#                     perfil=perfil_contenido,
#                     tiempo_generacion=tiempo_generacion
#                 )
#                 perfil.save()
            
#             # Convertir markdown a HTML si se solicita
#             formato = request.GET.get('formato', 'json')
#             if formato == 'html':
#                 html_content = markdown.markdown(perfil.perfil)
#                 return HttpResponse(html_content)
            
#             # Por defecto, devolver JSON
#             return JsonResponse({
#                 'documento': perfil.documento,
#                 'nombre': perfil.nombre,
#                 'total_casos': perfil.total_casos,
#                 'perfil': perfil.perfil,
#                 'fecha_creacion': perfil.fecha_creacion,
#                 'fecha_actualizacion': perfil.fecha_actualizacion,
#                 'tiempo_generacion': perfil.tiempo_generacion
#             })
                
#         except Exception as e:
#             return JsonResponse({
#                 'error': f'Error al generar perfil: {str(e)}',
#                 'documento': documento
#             }, status=500)
    
#     def generar_perfil(self, persona, noticias_spoa, noticias_rud):
#         """
#         Genera el contenido del perfil para una persona basado en sus datos y noticias criminales
#         """
#         # Ejemplo básico de generación de perfil
#         # En una implementación real, este método podría ser mucho más complejo
#         # o utilizar una API externa para generar el perfil
        
#         # Cargar un perfil de ejemplo desde el archivo perfiles_ejemplo.json
#         try:
#             with open('dashboard/data/perfiles_ejemplo.json', 'r', encoding='utf-8') as f:
#                 perfiles_ejemplo = json.load(f)
                
#             # Si el documento está en los ejemplos, usar ese perfil
#             if persona.numero_identificacion in perfiles_ejemplo:
#                 return perfiles_ejemplo[persona.numero_identificacion]['perfil']
#         except (FileNotFoundError, json.JSONDecodeError, KeyError):
#             pass
        
#         # Si no hay ejemplo, generar un perfil básico
#         perfil = f"""# PERFIL INTEGRAL - FISCALÍA GENERAL DE LA NACIÓN

# **1. DATOS PERSONALES**  
# - Documento: {persona.numero_identificacion}  
# - Nombre: {persona.nombre_completo}  
# - Total de casos: {len(noticias_spoa) + len(noticias_rud)}

# **2. CASOS ASOCIADOS**
# """
        
#         # Añadir información sobre los delitos
#         if persona.desaparcion_forzada:
#             perfil += "- Desaparición Forzada: Sí\n"
#         if persona.homicidio:
#             perfil += "- Homicidio: Sí\n"
#         if persona.secuestro:
#             perfil += "- Secuestro: Sí\n"
#         if persona.reclutamiento_ilicito:
#             perfil += "- Reclutamiento Ilícito: Sí\n"
#         if persona.rud:
#             perfil += "- Registrado en RUD: Sí\n"
        
#         # Añadir información sobre cada NUNC
#         if noticias_spoa:
#             perfil += "\n**3. NOTICIAS CRIMINALES**\n"
#             for i, noticia in enumerate(noticias_spoa):
#                 perfil += f"""
# - **NUNC {i+1}**: {noticia.nunc}
#   - Delito: {noticia.delito}
#   - Fecha hechos: {noticia.fecha_hechos if noticia.fecha_hechos else 'No registrada'}
#   - Fecha denuncia: {noticia.fecha_denuncia if noticia.fecha_denuncia else 'No registrada'}
#   - Fuente: {noticia.fuente}
#   - Unidad: {noticia.unidad}
# """
        
#         # Añadir información sobre RUD si aplica
#         if noticias_rud:
#             perfil += "\n**4. REGISTROS EN RUD**\n"
#             for i, rud in enumerate(noticias_rud):
#                 perfil += f"""
# - **Radicado {i+1}**: {rud.numero_radicado}
#   - Fecha desaparición: {rud.fecha_desaparicion if rud.fecha_desaparicion else 'No registrada'}
#   - Departamento: {rud.departamento_desaparicion}
#   - Municipio: {rud.municipio_desaparicion}
#   - Estado: {rud.estado_desaparicion}
# """
        
#         # Añadir recomendaciones generales
#         perfil += """
# **5. CONCLUSIONES Y RECOMENDACIONES**
# - Se recomienda verificar posibles conexiones entre los casos identificados
# - Revisar expedientes completos para obtener información adicional
# - Coordinar con otras unidades que manejan casos relacionados

# *Este perfil fue generado automáticamente y debe ser validado por un analista.*
# """
        
#         return perfil


# # Añadir vista para exportar perfil
# @csrf_exempt
# def exportar_perfil_pdf(request):
#     """
#     Vista para exportar el perfil a PDF
#     """
#     documento = request.GET.get('documento', '')
    
#     if not documento:
#         return JsonResponse({'error': 'Parámetro documento es requerido'}, status=400)
    
#     try:
#         # Obtener el perfil
#         perfil = PerfilPersona.objects.get(documento=documento)
        
#         # Convertir markdown a HTML
#         html_content = markdown.markdown(perfil.perfil)
        
#         # Crear respuesta con CSV
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="perfil_{documento}.pdf"'
        
#         # Plantilla HTML para el PDF
#         html_template = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="UTF-8">
#             <title>Resumen {perfil.nombre}</title>
#             <style>
#                 body {{ font-family: Arial, sans-serif; margin: 20px; }}
#                 h1 {{ color: #003366; }}
#                 h2, h3, h4 {{ color: #006699; }}
#                 .header {{ text-align: center; margin-bottom: 30px; }}
#                 .content {{ line-height: 1.5; }}
#                 .footer {{ margin-top: 30px; font-size: 0.8em; text-align: center; color: #666; }}
#             </style>
#         </head>
#         <body>
#             <div class="header">
#                 <h1>RESUMEN INTEGRAL - FISCALÍA GENERAL DE LA NACIÓN</h1>
#                 <p>Fecha de generación: {perfil.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')}</p>
#             </div>
#             <div class="content">
#                 {html_content}
#             </div>
#             <div class="footer">
#                 <p>Documento generado por el sistema de perfiles de la Fiscalía General de la Nación</p>
#             </div>
#         </body>
#         </html>
#         """
        
#         # Generar PDF
#         pisa_status = pisa.CreatePDF(html_template, dest=response)
        
#         # Si hay error
#         if pisa_status.err:
#             return JsonResponse({'error': 'Error al generar PDF'}, status=500)
        
#         return response
        
#     except PerfilPersona.DoesNotExist:
#         return JsonResponse({'error': 'Perfil no encontrado'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': f'Error: {str(e)}'}, status=500)
