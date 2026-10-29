from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dental/', views.dental, name='dental'),
    path('pediatric/', views.pediatric, name='pediatric'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact/', views.contact, name='contact'),

    # Lean CRM Dashboard
    path('crm/', views.crm_dashboard, name='crm'),
    path('crm-dashboard/', views.crm_dashboard, name='crm_dashboard'),

    # Request-Based Booking API & Status Updater
    path('api/book/', views.api_book, name='api_book'),
    path('api/requests/<int:pk>/status/', views.api_update_request_status, name='api_update_request_status'),
]
