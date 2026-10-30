from django.urls import path
from . import views

urlpatterns = [
    # Public Clinic Website
    path('', views.home, name='home'),
    path('dental/', views.dental, name='dental'),
    path('pediatric/', views.pediatric, name='pediatric'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact/', views.contact, name='contact'),

    # Request-Based Booking API & Status Updater
    path('api/book/', views.api_book, name='api_book'),
    path('api/requests/<int:pk>/status/', views.api_update_request_status, name='api_update_request_status'),

    # ---------------------------------------------
    # HEALTHCARE SAAS CRM & ROLE-BASED DASHBOARDS
    # ---------------------------------------------
    # Authentication & Session
    path('crm/login/', views.crm_login, name='crm_login'),
    path('crm/logout/', views.crm_logout, name='crm_logout'),
    path('crm/quick-switch/<str:target_role>/', views.crm_quick_switch, name='crm_quick_switch'),

    # Dynamic Dispatcher
    path('crm/', views.crm_hub, name='crm_hub'),
    path('crm-dashboard/', views.crm_hub, name='crm_dashboard_legacy'),

    # Role Dashboards
    path('crm/frontdesk/', views.crm_frontdesk_dashboard, name='crm_frontdesk'),
    path('crm/dental/', views.crm_dental_dashboard, name='crm_dental'),
    path('crm/pediatric/', views.crm_pediatric_dashboard, name='crm_pediatric'),
    path('crm/admin/', views.crm_admin_dashboard, name='crm_admin'),

    # Printable Documents
    path('crm/pediatric/vaccination-card/<int:patient_id>/', views.crm_vaccination_card, name='crm_vaccination_card'),
    path('crm/invoice/<int:invoice_id>/print/', views.crm_invoice_print, name='crm_invoice_print'),

    # Interactive AJAX / JSON Endpoints
    path('crm/api/queue/status/', views.api_queue_update, name='api_queue_update'),
    path('crm/api/queue/add/', views.api_queue_add, name='api_queue_add'),
    path('crm/api/family/add/', views.api_family_add, name='api_family_add'),
    path('crm/api/patient/add/', views.api_patient_add, name='api_patient_add'),
    path('crm/api/invoice/create/', views.api_invoice_create, name='api_invoice_create'),
    path('crm/api/dental/tooth-update/', views.api_dental_tooth_update, name='api_dental_tooth_update'),
    path('crm/api/dental/treatment-plan/add/', views.api_dental_plan_add, name='api_dental_plan_add'),
    path('crm/api/dental/lab-order/add/', views.api_dental_lab_add, name='api_dental_lab_add'),
    path('crm/api/pediatric/growth/add/', views.api_pediatric_growth_add, name='api_pediatric_growth_add'),
    path('crm/api/pediatric/vaccine/update/', views.api_pediatric_vaccine_update, name='api_pediatric_vaccine_update'),
    path('crm/api/pediatric/dose-helper/', views.api_pediatric_dose_helper, name='api_pediatric_dose_helper'),
    path('crm/api/prescription/create/', views.api_prescription_create, name='api_prescription_create'),
    path('crm/api/admin/staff/add/', views.api_admin_staff_add, name='api_admin_staff_add'),
    path('crm/api/admin/export/<str:format_type>/', views.api_admin_export, name='api_admin_export'),
]
