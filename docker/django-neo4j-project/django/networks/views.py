from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json

from .services import get_component_info, get_neighbors

# Create your views here.

class NetworkVisualizationView(LoginRequiredMixin, TemplateView):
    """
    Vista para visualizar redes
    """
    template_name = 'networks/visualization.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el node_id de los parámetros de ruta
        node_id = self.kwargs.get('node_id', '')  # Corrección: usar self.kwargs en lugar de self.request.GET
        view_type = self.request.GET.get('type', 'component')
        
        context['node_id'] = node_id
        context['view_type'] = view_type
        
        return context


class ApiComponentInfoView(LoginRequiredMixin, View):
    """
    API para obtener información de la componente de un nodo
    """
    def get(self, request):
        node_id = request.GET.get('node_id', '')
        limit = int(request.GET.get('limit', 1000))
        
        if not node_id:
            return JsonResponse({'error': 'Se requiere un ID de nodo'}, status=400)
        
        # Obtener información de la componente
        component_info = get_component_info(node_id, limit)
        print(component_info)
        
        return JsonResponse(component_info)


class ApiNeighborsView(LoginRequiredMixin, View):
    """
    API para obtener los vecinos de un nodo
    """
    def get(self, request):
        node_id = request.GET.get('node_id', '')
        depth = int(request.GET.get('depth', 1))
        limit = int(request.GET.get('limit', 100))
        
        if not node_id:
            return JsonResponse({'error': 'Se requiere un ID de nodo'}, status=400)
        
        # Obtener vecinos
        neighbors_info = get_neighbors(node_id, depth, limit)
        
        return JsonResponse(neighbors_info)