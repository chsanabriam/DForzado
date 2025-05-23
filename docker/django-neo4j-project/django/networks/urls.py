from django.urls import path
from . import views

app_name = 'networks'

urlpatterns = [
    path('visualization/<str:node_id>/', views.NetworkVisualizationView.as_view(), name='visualization'),
    path('api/component/', views.ApiComponentInfoView.as_view(), name='api_component'),
]