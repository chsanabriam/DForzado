
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Vista principal del dashboard
    path('', views.DashboardView.as_view(), name='index'),
    
    # Vistas detalladas para cada distribución
    path('distribucion-fuente/', views.DistribucionPorFuenteView.as_view(), name='distribucion_fuente'),
    path('distribucion-unidad/', views.DistribucionPorUnidadView.as_view(), name='distribucion_unidad'),
    
    # APIs para obtener datos en formato JSON
    path('api/fuentes/', views.DatosGraficasFuenteAPIView.as_view(), name='api_fuentes'),
    path('api/unidades/', views.DatosGraficasUnidadAPIView.as_view(), name='api_unidades'),
]