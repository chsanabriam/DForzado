from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json

from .models import ConsolidadoSpoa, PersonasDf
from .utils import obtener_distribucion_por_fuente, obtener_distribucion_por_unidad

class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del dashboard que muestra las gráficas de distribución
    """
    template_name = 'dashboard/pages/dashboard.html'
    login_url = '/admin/login/'  # Redirige a la página de login si no está autenticado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener datos para las gráficas
        context['total_spoa'] = ConsolidadoSpoa.objects.count()
        context['total_personas'] = PersonasDf.objects.count()
        
        # Datos para gráfica de distribución por fuente
        fuentes = obtener_distribucion_por_fuente()
        context['fuentes_labels'] = json.dumps([item['fuente'] for item in fuentes])
        context['fuentes_data'] = json.dumps([item['cantidad'] for item in fuentes])
        
        # Datos para gráfica de distribución por unidad
        unidades = obtener_distribucion_por_unidad()
        context['unidades_labels'] = json.dumps([item['unidad'] for item in unidades])
        context['unidades_data'] = json.dumps([item['cantidad'] for item in unidades])
        
        return context


class DistribucionPorFuenteView(LoginRequiredMixin, TemplateView):
    """
    Vista para mostrar la gráfica detallada de distribución por fuente
    """
    template_name = 'dashboard/pages/distribucion_fuente.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener datos para las gráficas
        fuentes = obtener_distribucion_por_fuente()
        context['fuentes'] = fuentes
        context['fuentes_labels'] = json.dumps([item['fuente'] for item in fuentes])
        context['fuentes_data'] = json.dumps([item['cantidad'] for item in fuentes])
        
        return context


class DistribucionPorUnidadView(LoginRequiredMixin, TemplateView):
    """
    Vista para mostrar la gráfica detallada de distribución por unidad
    """
    template_name = 'dashboard/pages/distribucion_unidad.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener datos para las gráficas
        unidades = obtener_distribucion_por_unidad()
        context['unidades'] = unidades
        context['unidades_labels'] = json.dumps([item['unidad'] for item in unidades])
        context['unidades_data'] = json.dumps([item['cantidad'] for item in unidades])
        
        return context


class DatosGraficasFuenteAPIView(LoginRequiredMixin, TemplateView):
    """
    Vista API para obtener datos de distribución por fuente en formato JSON
    """
    def get(self, request, *args, **kwargs):
        fuentes = obtener_distribucion_por_fuente()
        data = {
            'labels': [item['fuente'] for item in fuentes],
            'data': [item['cantidad'] for item in fuentes]
        }
        return JsonResponse(data)


class DatosGraficasUnidadAPIView(LoginRequiredMixin, TemplateView):
    """
    Vista API para obtener datos de distribución por unidad en formato JSON
    """
    def get(self, request, *args, **kwargs):
        unidades = obtener_distribucion_por_unidad()
        data = {
            'labels': [item['unidad'] for item in unidades[:10]],
            'data': [item['cantidad'] for item in unidades[:10]]
        }
        
        print(data)
        return JsonResponse(data)