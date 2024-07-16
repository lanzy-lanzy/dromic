from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('overview/', views.overview, name='overview'),
    path('disaster-info/', views.disaster_info, name='disaster_info'),
    
    path('evacuation-centers/', views.evacuation_centers, name='evacuation_centers'),

  
    path('save_report/', views.save_report, name='save_report'),
    
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/export-pdf/', views.export_report_pdf, name='export_report_pdf'),

    path('affected-areas/', views.affected_area_list, name='affected_area_list'),
    path('add-affected-area/', views.add_affected_area, name='add_affected_area'),
    
    path('get-municipalities/', views.get_municipalities, name='get_municipalities'),
    path('get-barangays/', views.get_barangays, name='get_barangays'),
    
    path('disaster-info/', views.disaster_info, name='disaster_info'),
    path('api/disasters/', views.get_disasters, name='get_disasters'),
    path('api/disasters/create/', views.create_disaster, name='create_disaster'),
]