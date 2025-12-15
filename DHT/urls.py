from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Page principale - Dashboard
    path('', views.dashboard, name='dashboard'),

    # Pages graphiques
    path('graph_temp/', views.graph_temp, name='graph_temp'),
    path('graph_hum/', views.graph_hum, name='graph_hum'),

    # API endpoints
    path('api/', api.Dlist, name='api_list'),
    path('api/post/', api.Dhtviews.as_view(), name='api_post'),
    path('latest/', views.latest_json, name='latest_json'),

    # API données graphiques
    path('chart-data/', views.chart_data, name='chart_data'),
    path('chart-data-jour/', views.chart_data_jour, name='chart_data_jour'),
    path('chart-data-semaine/', views.chart_data_semaine, name='chart_data_semaine'),
    path('chart-data-mois/', views.chart_data_mois, name='chart_data_mois'),

    # Utilitaires
    path('download_csv/', views.download_csv, name='download_csv'),

    # Pages anciennes (compatibilité)
    path('index/', views.table, name='table'),
    path('myChart/', views.graphique, name='myChart'),
    path('incident-status/', views.incident_status, name='incident_status'),
    path('update-incident/', views.update_incident, name='update_incident'),
    path('archive-incidents/', views.archive_incidents, name='archive_incidents'),

# Incidents
    path('incident-status/', views.incident_status, name='incident_status'),
    path('update-incident/', views.update_incident, name='update_incident'),
    path('archive-incidents/', views.archive_incidents, name='archive_incidents'),
    path('api/check-create-incident/', views.check_create_incident, name='check_create_incident'),
    path('download_incidents_excel/', views.download_incidents_excel, name='download_incidents_excel'),

    # Manual data entry
    path('api/manual-entry/', views.manual_data_entry, name='manual_data_entry'),
]