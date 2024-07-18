from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('overview/', views.overview, name='overview'),
    path('disaster-info/', views.disaster_info, name='disaster_info'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('evacuation-centers-list/', views.evacuation_center_list, name='evacuation_center_list'),
     path('add-evacuation-center/', views.add_evacuation_center, name='add_evacuation_center'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

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

    path('create_disaster/', views.create_disaster, name='create_disaster'),
    path('create_province/', views.create_province, name='create_province'),
    path('create_municipality/', views.create_municipality, name='create_municipality'),
    path('create_barangay/', views.create_barangay, name='create_barangay'),
    
    
    path('disaster_impact/', views.disaster_impact, name='disaster_impact'),
    # Other URL patterns
    

]