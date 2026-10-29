from django.contrib import admin
from .models import AppointmentRequest, Lead, Appointment, PatientIntake, WorkflowLog


@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'clinic_type', 'phone_number', 'preferred_date', 'preferred_time', 'status', 'created_at')
    list_filter = ('clinic_type', 'status', 'created_at')
    search_fields = ('patient_name', 'parent_name', 'phone_number', 'service_needed')
    list_editable = ('status',)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('crm_id', 'full_name', 'phone', 'service_interest', 'pain_level', 'status', 'created_at')
    search_fields = ('crm_id', 'full_name', 'phone', 'email')
    list_filter = ('status', 'service_interest', 'created_at')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'patient_name', 'doctor', 'appointment_date', 'appointment_time', 'crm_sync_status')
    search_fields = ('booking_ref', 'patient_name', 'phone', 'email')
    list_filter = ('doctor', 'crm_sync_status')


@admin.register(PatientIntake)
class PatientIntakeAdmin(admin.ModelAdmin):
    list_display = ('intake_ref', 'full_name', 'phone', 'insurance_provider', 'dental_anxiety_level')
    search_fields = ('intake_ref', 'full_name', 'phone')


@admin.register(WorkflowLog)
class WorkflowLogAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'recipient', 'channel', 'status', 'created_at')
    list_filter = ('channel', 'status')
