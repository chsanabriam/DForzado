from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Vistas principales del dashboard
    path('', views.DashboardView.as_view(), name='index'),
    path('distribucion-fuente/', views.DistribucionPorFuenteView.as_view(), name='distribucion_fuente'),
    path('distribucion-unidad/', views.DistribucionPorUnidadView.as_view(), name='distribucion_unidad'),
    path('personas/', views.PersonasView.as_view(), name='personas'), 
    
    # API para datos dinámicos
    path('api/registros-por-fuente/', views.ApiRegistrosPorFuenteView.as_view(), name='api_registros_por_fuente'),
    path('api/registros-por-seccional/', views.ApiRegistrosPorSeccionalView.as_view(), name='api_registros_por_seccional'),
    path('api/unidades-por-seccional/', views.ApiUnidadesPorSeccionalView.as_view(), name='api_unidades_por_seccional'),
    path('api/despachos-por-seccional/', views.ApiDespachosPorSeccionalView.as_view(), name='api_despachos_por_seccional'),
    path('api/registros-por-necropsia/', views.ApiRegistrosPorNecropsiaView.as_view(), name='api_registros_por_necropsia'),
    path('api/detalle-registro/', views.ApiDetalleRegistroView.as_view(), name='api_detalle_registro'),
    path('api/intersecciones-delito/', views.ApiInterseccionesDelitoView.as_view(), name='api_intersecciones_delito'),
    path('api/dashboard-data/', views.ApiDashboardDataView.as_view(), name='api_dashboard_data'),
    path('api/check-updates/', views.ApiCheckUpdatesView.as_view(), name='api_check_updates'),
    
    # API para personas
    # Nuevas APIs
    path('api/personas/', views.ApiPersonasFiltradas.as_view(), name='api_personas'),
    path('api/noticias/', views.ApiNoticiasCriminalesPorPersona.as_view(), name='api_noticias'),
    path('api/timeline/', views.ApiLineaTiempoPorPersona.as_view(), name='api_timeline'),
    
    # Nueva API para perfiles
    path('api/perfil/', views.ApiPerfilPersonaView.as_view(), name='api_perfil'),
    path('api/perfil/exportar-pdf/', views.exportar_perfil_pdf, name='exportar_perfil_pdf'),
    
    # Nueva ruta para API de funcionario (versión simplificada)
    path('api/funcionario/', views.ApiFuncionarioView.as_view(), name='api_funcionario'),

]