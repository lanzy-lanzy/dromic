from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('overview/', views.overview, name='overview'),
    path('disaster-info/', views.disaster_info, name='disaster_info'),
    path('affected-areas/', views.affected_areas, name='affected_areas'),
    path('evacuation-centers/', views.evacuation_centers, name='evacuation_centers'),
    path('reports/', views.reports, name='reports'),
    path('logout/', views.logout_view, name='logout'),
]