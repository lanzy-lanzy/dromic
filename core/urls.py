from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('overview/', views.overview, name='overview'),
    path('disaster-info/', views.disaster_info, name='disaster_info'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('evacuation-centers-list/', views.evacuation_center_list, name='evacuation_center_list'),
     path('add-evacuation-center/', views.add_evacuation_center, name='add_evacuation_center'),
    path('api/evacuation-centers/', views.get_evacuation_centers, name='get_evacuation_centers'),
    path('api/evacuation-centers/<int:center_id>/delete/', views.delete_evacuation_center, name='delete_evacuation_center'),
    path('api/evacuation-centers/bulk-delete/', views.bulk_delete_evacuation_centers, name='bulk_delete_evacuation_centers'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('save_report/', views.save_report, name='save_report'),
    
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/export-pdf/', views.export_report_pdf, name='export_report_pdf'),

    path('affected-areas/', views.affected_area_list, name='affected_area_list'),
    path('add-affected-area/', views.add_affected_area, name='add_affected_area'),
    path('api/affected-areas/', views.get_affected_areas, name='get_affected_areas'),
    path('api/affected-areas/<int:area_id>/delete/', views.delete_affected_area, name='delete_affected_area'),
    path('api/affected-areas/bulk-delete/', views.bulk_delete_affected_areas, name='bulk_delete_affected_areas'),
    
    path('get-municipalities/', views.get_municipalities, name='get_municipalities'),
    path('get-barangays/', views.get_barangays, name='get_barangays'),
    
    path('disaster-info/', views.disaster_info, name='disaster_info'),
    path('api/disasters/', views.get_disasters, name='get_disasters'),
    path('api/disasters/create/', views.create_disaster, name='create_disaster'),
    path('api/disasters/<int:disaster_id>/delete/', views.delete_disaster, name='delete_disaster'),
    path('api/disasters/bulk-delete/', views.bulk_delete_disasters, name='bulk_delete_disasters'),

    path('create_disaster/', views.create_disaster, name='create_disaster'),
    path('create_province/', views.create_province, name='create_province'),
    path('create_municipality/', views.create_municipality, name='create_municipality'),
    path('create_barangay/', views.create_barangay, name='create_barangay'),
    
    
    path('disaster_impact/', views.disaster_impact, name='disaster_impact'),
    # Other URL patterns
    
     path('api/add_family_member', views.add_family_member, name='add_family_member'),
    path('api/add_displaced_population', views.add_displaced_population, name='add_displaced_population'),
]