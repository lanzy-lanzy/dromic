from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('overview/', views.overview, name='overview'),
    path('disaster-info/', views.disaster_info, name='disaster_info'),
    path('affected-areas/', views.affected_areas, name='affected_areas'),
    path('evacuation-centers/', views.evacuation_centers, name='evacuation_centers'),

    path('logout/', views.logout_view, name='logout'),
    path('save_report/', views.save_report, name='save_report'),
    
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/export-pdf/', views.export_report_pdf, name='export_report_pdf'),

]