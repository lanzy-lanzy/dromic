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
    path('affected-areas/export-pdf/', views.export_affected_areas_pdf, name='export_affected_areas_pdf'),
    path('add-affected-area/', views.add_affected_area, name='add_affected_area'),
    path('api/affected-areas/<int:area_id>/edit/', views.edit_affected_area, name='edit_affected_area'),
    path('api/affected-areas/', views.get_affected_areas, name='get_affected_areas'),
    path('api/affected-areas/<int:area_id>/delete/', views.delete_affected_area, name='delete_affected_area'),
    path('api/affected-areas/bulk-delete/', views.bulk_delete_affected_areas, name='bulk_delete_affected_areas'),
    
    path('get-municipalities/', views.get_municipalities, name='get_municipalities'),
    path('get-barangays/', views.get_barangays, name='get_barangays'),
    
    path('disaster-info/', views.disaster_info, name='disaster_info'),
    path('api/disasters/', views.get_disasters, name='get_disasters'),
    path('api/disasters/create/', views.create_disaster, name='create_disaster'),
    path('api/disasters/<int:disaster_id>/update/', views.edit_disaster, name='edit_disaster'),
    path('api/disasters/<int:disaster_id>/delete/', views.delete_disaster, name='delete_disaster'),
    path('api/disasters/bulk-delete/', views.bulk_delete_disasters, name='bulk_delete_disasters'),

    path('create_disaster/', views.create_disaster, name='create_disaster'),
    path('create_province/', views.create_province, name='create_province'),
    path('create_municipality/', views.create_municipality, name='create_municipality'),
    path('create_barangay/', views.create_barangay, name='create_barangay'),
    
    
    path('disaster_impact/', views.disaster_impact, name='disaster_impact'),
    
    # Relief Operations
    path('relief-operations/', views.relief_operations_view, name='relief_operations'),
    path('relief-operations/export-pdf/', views.export_relief_operations_pdf, name='export_relief_operations_pdf'),
    path('api/relief-operations/', views.get_relief_operations, name='get_relief_operations'),
    path('api/relief-operations/add/', views.add_relief_operation, name='add_relief_operation'),
    path('api/relief-operations/<int:op_id>/delete/', views.delete_relief_operation, name='delete_relief_operation'),
    
    # Distribution Tracking
    path('relief-operations/<int:op_id>/distribution/', views.relief_operation_distribution_view, name='relief_operation_distribution'),
    path('api/relief-operations/<int:op_id>/distribution/', views.get_distribution_families, name='get_distribution_families'),
    path('api/relief-operations/<int:op_id>/toggle-distribution/', views.toggle_family_distribution, name='toggle_family_distribution'),
    path('relief-operations/<int:op_id>/export-rds/', views.export_rds_pdf, name='export_rds_pdf'),
    
    # Family Management
    path('families/', views.family_list, name='family_list'),
    path('families/export-pdf/', views.export_families_pdf, name='export_families_pdf'),
    path('api/families/', views.get_families, name='get_families'),
    path('api/families/add/', views.add_family, name='add_family'),
    path('api/families/<int:family_id>/delete/', views.delete_family, name='delete_family'),
    path('api/families/<int:family_id>/edit/', views.edit_family, name='edit_family'),
    
    # Family Members Management
    path('api/families/<int:family_id>/members/', views.get_family_members, name='get_family_members'),
    path('api/families/<int:family_id>/members/add/', views.add_family_member, name='add_family_member'),
    path('api/members/<int:member_id>/edit/', views.edit_family_member, name='edit_family_member'),
    path('api/members/<int:member_id>/delete/', views.delete_family_member, name='delete_family_member'),

    # Early Recovery
    path('early-recovery/', views.early_recovery_view, name='early_recovery'),
    path('api/early-recovery/', views.get_early_recoveries, name='get_early_recoveries'),
    path('api/early-recovery/add/', views.add_early_recovery, name='add_early_recovery'),
    path('api/early-recovery/<int:rec_id>/delete/', views.delete_early_recovery, name='delete_early_recovery'),
    
    # Other URL patterns
]