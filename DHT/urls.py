from django.urls import path
from . import views
from . import api

urlpatterns = [
    path("api/",api.Dlist,name='json'),
    path("api/post",api.Dhtviews.as_view(),name='json'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('index/',views.table,name='table'),
    path('myChart/',views.graphique,name='myChart'),
    path('',views.dashboard,name='dashboard'),
    path("latest/", views.latest_json, name="latest_json"),
    ]