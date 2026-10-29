import json
import urllib.parse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from .models import AppointmentRequest, Lead, Appointment, PatientIntake, WorkflowLog


def ensure_demo_requests():
    """Seeds a few realistic Wanowrie requests if database is empty."""
    if AppointmentRequest.objects.count() == 0:
        AppointmentRequest.objects.create(
            clinic_type='dental',
            patient_name='Rahul Kulkarni',
            parent_name='',
            phone_number='9822012345',
            service_needed='Root Canal Treatment',
            preferred_date='Tomorrow, 11:30 AM',
            preferred_time='Morning (10:00 AM - 1:00 PM)',
            notes='Mild pain in upper right molar. Prefers Dr. Sabina.',
            status='pending',
        )
        AppointmentRequest.objects.create(
            clinic_type='pediatric',
            patient_name='Aarav Mehta (4 yrs)',
            parent_name='Sneha Mehta',
            phone_number='9890123456',
            service_needed='Vaccination & Growth Checkup',
            preferred_date='Friday, 4:00 PM',
            preferred_time='Evening (4:00 PM - 8:00 PM)',
            notes='Needs MMR booster dose. Please confirm slot with Dr. Jalil.',
            status='pending',
        )
        AppointmentRequest.objects.create(
            clinic_type='dental',
            patient_name='Pooja Deshmukh',
            parent_name='',
            phone_number='9765432109',
            service_needed='Cosmetic Smile Makeover',
            preferred_date='Saturday, 12:00 PM',
            preferred_time='Morning (10:00 AM - 1:00 PM)',
            notes='Consultation for clear aligners / veneers.',
            status='accepted',
        )
        AppointmentRequest.objects.create(
            clinic_type='pediatric',
            patient_name='Ananya Joshi (11 mos)',
            parent_name='Vikram Joshi',
            phone_number='9823456780',
            service_needed='Newborn & Infant Nutrition',
            preferred_date='Saturday, 5:30 PM',
            preferred_time='Evening (4:00 PM - 8:00 PM)',
            notes='Weaning food guidance and sleep schedule.',
            status='reschedule',
        )


# ----------------- PUBLIC WEBSITE VIEWS -----------------

def home(request):
    ensure_demo_requests()
    return render(request, 'home.html', {
        'initial_clinic': 'dental',
        'is_home': True,
    })


def dental(request):
    return render(request, 'home.html', {
        'initial_clinic': 'dental',
        'is_dental': True,
    })


def pediatric(request):
    return render(request, 'pediatric.html', {
        'initial_clinic': 'pediatric',
        'is_pediatric': True,
    })


def about(request):
    return render(request, 'about.html')


def gallery(request):
    return render(request, 'gallery.html')


def contact(request):
    return render(request, 'contact.html')


# ----------------- FRONT DESK LEAN CRM -----------------

def crm_dashboard(request):
    ensure_demo_requests()
    status_filter = request.GET.get('status', 'all')
    clinic_filter = request.GET.get('clinic', 'all')

    requests_qs = AppointmentRequest.objects.all()

    if status_filter in ['pending', 'accepted', 'reschedule', 'cancelled']:
        requests_qs = requests_qs.filter(status=status_filter)
    if clinic_filter in ['dental', 'pediatric']:
        requests_qs = requests_qs.filter(clinic_type=clinic_filter)

    total_count = AppointmentRequest.objects.count()
    pending_count = AppointmentRequest.objects.filter(status='pending').count()
    accepted_count = AppointmentRequest.objects.filter(status='accepted').count()
    reschedule_count = AppointmentRequest.objects.filter(status='reschedule').count()
    dental_count = AppointmentRequest.objects.filter(clinic_type='dental').count()
    pediatric_count = AppointmentRequest.objects.filter(clinic_type='pediatric').count()

    return render(request, 'crm_dashboard.html', {
        'requests': requests_qs,
        'current_status': status_filter,
        'current_clinic': clinic_filter,
        'total_count': total_count,
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'reschedule_count': reschedule_count,
        'dental_count': dental_count,
        'pediatric_count': pediatric_count,
    })


# ----------------- AJAX / API ENDPOINTS -----------------

@csrf_exempt
@require_POST
def api_book(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    clinic_type = data.get('clinic_type', 'dental')
    patient_name = data.get('patient_name', '').strip()
    parent_name = data.get('parent_name', '').strip()
    phone_number = data.get('phone_number', '').strip()
    service_needed = data.get('service_needed', '').strip() or ('Dental Consultation' if clinic_type == 'dental' else 'Pediatric Consultation')
    preferred_date = data.get('preferred_date', '').strip()
    preferred_time = data.get('preferred_time', '').strip() or 'Morning (10:00 AM - 1:00 PM)'
    notes = data.get('notes', '').strip()

    if not patient_name:
        return JsonResponse({'status': 'error', 'message': 'Patient name is required.'}, status=400)
    if not phone_number:
        return JsonResponse({'status': 'error', 'message': 'Phone number is required.'}, status=400)
    if not preferred_date:
        return JsonResponse({'status': 'error', 'message': 'Preferred date is required.'}, status=400)

    appointment_req = AppointmentRequest.objects.create(
        clinic_type=clinic_type,
        patient_name=patient_name,
        parent_name=parent_name,
        phone_number=phone_number,
        service_needed=service_needed,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        notes=notes,
        status='pending'
    )

    # Optional: Log action to WorkflowLog for CRM audit
    WorkflowLog.objects.create(
        event_type="New Web Appointment Request",
        recipient=phone_number,
        channel="Web Booking Engine",
        workflow_step=f"Queued for {clinic_type.capitalize()} Clinic front desk WhatsApp confirmation",
        payload_preview=f"Patient: {patient_name}, Date: {preferred_date} {preferred_time}",
        status="Pending Front Desk Action",
        scheduled_for=preferred_date
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Appointment request received! Our front desk will confirm your exact time via WhatsApp shortly.',
        'request_id': appointment_req.id,
        'clinic_type': appointment_req.clinic_type,
        'patient_name': appointment_req.patient_name,
        'whatsapp_url': appointment_req.whatsapp_accept_url()
    })


@csrf_exempt
@require_POST
def api_update_request_status(request, pk):
    req_obj = get_object_or_404(AppointmentRequest, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
        new_status = data.get('status')
    except Exception:
        new_status = request.POST.get('status')

    if new_status in ['pending', 'accepted', 'reschedule', 'cancelled']:
        req_obj.status = new_status
        req_obj.save(update_fields=['status'])
        return JsonResponse({
            'status': 'success',
            'new_status': req_obj.status,
            'message': f'Status updated to {req_obj.get_status_display()}'
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid status choice.'}, status=400)
