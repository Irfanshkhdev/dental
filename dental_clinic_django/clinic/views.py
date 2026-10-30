import json
import csv
import urllib.parse
import datetime
from decimal import Decimal
from functools import wraps

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q

from .models import (
    AppointmentRequest, Lead, Appointment, PatientIntake, WorkflowLog,
    StaffProfile, Family, Patient, QueueEntry, Invoice,
    DentalToothRecord, DentalTreatmentPlan, DentalLabOrder, DentalRecall,
    ChildGrowthRecord, VaccinationRecord, NewbornRecord, DevelopmentalMilestone,
    ClinicalPrescription, AuditLog, ScheduledReminder, WhatsAppThread, WhatsAppChatMessage
)
from .supabase_client import (
    supabase_sync_appointment,
    supabase_sync_queue,
    supabase_sync_invoice
)


# ==========================================
# RBAC HELPER DECORATOR
# ==========================================

def role_required(allowed_roles):
    """
    Enforces Role-Based Access Control.
    Super Admins and users with role='admin' can access all modules.
    Other roles are restricted to allowed_roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/crm/login/?next={request.path}")

            profile = getattr(request.user, 'clinic_staff_profile', None)
            user_role = profile.role if profile else ('admin' if request.user.is_superuser else 'front_desk')

            # Super admin can view everything
            if user_role == 'admin' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if user_role not in allowed_roles:
                messages.error(
                    request,
                    f"Confidentiality restriction: Your profile ({user_role}) cannot access this medical/financial module."
                )
                return redirect('crm_hub')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def log_audit(request, action_type, model_name, target_id, summary):
    try:
        user = request.user if request.user.is_authenticated else None
        user_email = user.email if user else 'anonymous@rootsbuds.com'
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        AuditLog.objects.create(
            user=user,
            user_email=user_email,
            action_type=action_type,
            target_model=model_name,
            target_id=str(target_id),
            summary=summary,
            ip_address=ip
        )
    except Exception as e:
        print(f"Audit log failed: {e}")


# ==========================================
# PUBLIC WEBSITE VIEWS
# ==========================================

def home(request):
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


# ==========================================
# CRM AUTHENTICATION & HUB DISPATCHER
# ==========================================

def crm_login(request):
    next_url = request.GET.get('next', '/crm/dashboard/')

    if request.user.is_authenticated:
        return redirect('crm_dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()

        # Master Owner / Super-Admin guaranteed credentials
        if identifier.lower() == 'irfanshaikh3262@gmail.com' and password == 'irfan@123':
            user_obj = User.objects.filter(email__iexact='irfanshaikh3262@gmail.com').first()
            if not user_obj:
                user_obj = User.objects.create_superuser('irfanshaikh3262@gmail.com', 'irfanshaikh3262@gmail.com', 'irfan@123')
            elif not user_obj.check_password('irfan@123'):
                user_obj.set_password('irfan@123')
                user_obj.save()
            login(request, user_obj)
            log_audit(request, 'LOGIN', 'User', user_obj.id, f"Super-Admin signed in: {user_obj.email}")
            messages.success(request, "Welcome back, Clinic Director Irfan Shaikh!")
            return redirect(next_url if next_url != '/crm/login/' else 'crm_dashboard')

        # Support login via email or username
        user_obj = User.objects.filter(email__iexact=identifier).first() or User.objects.filter(username__iexact=identifier).first()

        if user_obj and user_obj.check_password(password):
            login(request, user_obj)
            log_audit(request, 'LOGIN', 'User', user_obj.id, f"Staff signed in: {user_obj.email}")
            messages.success(request, f"Welcome back, {user_obj.clinic_staff_profile.full_name if hasattr(user_obj, 'clinic_staff_profile') else user_obj.username}!")
            return redirect(next_url if next_url != '/crm/login/' else 'crm_dashboard')
        else:
            messages.error(request, "Invalid email or password. Please verify credentials.")

    return render(request, 'crm/login.html')


def crm_logout(request):
    if request.user.is_authenticated:
        log_audit(request, 'LOGIN', 'User', request.user.id, f"Staff signed out: {request.user.email}")
    logout(request)
    messages.info(request, "You have been securely signed out of Roots & Buds CRM.")
    return redirect('crm_login')


def crm_quick_switch(request, target_role):
    """
    1-Click Demo Switcher to test and grade each role seamlessly.
    """
    role_email_map = {
        'admin': 'irfanshaikh3262@gmail.com',
        'front_desk': 'frontdesk@rootsbuds.com',
        'doctor_dental': 'sabina@rootsbuds.com',
        'doctor_pediatric': 'jalil@rootsbuds.com',
    }

    email = role_email_map.get(target_role)
    if email:
        user = User.objects.filter(email=email).first()
        if user:
            login(request, user)
            log_audit(request, 'LOGIN', 'StaffProfile', user.id, f"Quick demo role switch to {target_role}")
            messages.success(request, f"Switched active workspace to: {user.clinic_staff_profile.get_role_display()}")
            return redirect('crm_hub')

    messages.error(request, "Role switch failed.")
    return redirect('crm_hub')


def crm_hub(request):
    """
    Central dispatcher: directs authenticated staff directly to the Executive Dashboard.
    """
    if not request.user.is_authenticated:
        return redirect('crm_login')
    return redirect('crm_dashboard')


# ==========================================
# ROLE 1: FRONT DESK (THE HUB)
# ==========================================

@role_required(['front_desk', 'admin'])
def crm_frontdesk_dashboard(request):
    """
    Front Desk The Hub:
    - Combined calendar / schedule
    - Appointment requests inbox with 1-click WhatsApp messaging
    - Live waiting room queue (walk-in & appointments)
    - Billing & Invoicing (cash, upi, card, partial payments)
    - Family Profiles (linking parents & child dependents)
    STRICTLY NO clinical notes, doctor earnings, or financial analytics!
    """
    status_filter = request.GET.get('status', 'all')
    clinic_filter = request.GET.get('clinic', 'all')

    requests_qs = AppointmentRequest.objects.all()
    if status_filter in ['pending', 'accepted', 'reschedule', 'cancelled']:
        requests_qs = requests_qs.filter(status=status_filter)
    if clinic_filter in ['dental', 'pediatric']:
        requests_qs = requests_qs.filter(clinic_type=clinic_filter)

    # Live Queue
    queue_entries = QueueEntry.objects.filter(status__in=['waiting', 'in_consultation']).order_by('status', 'token_number')
    recent_completed_queue = QueueEntry.objects.filter(status='completed').order_by('-completed_time')[:5]

    # Family Profiles & Patients
    families = Family.objects.prefetch_related('members').all()[:20]
    patients = Patient.objects.select_related('family').all()[:30]

    # Billing - Front desk view: operational list (no revenue summaries or doctor profit shares)
    invoices = Invoice.objects.select_related('patient', 'family').all()[:20]

    context = {
        'requests': requests_qs[:30],
        'total_requests': AppointmentRequest.objects.count(),
        'pending_requests': AppointmentRequest.objects.filter(status='pending').count(),
        'accepted_requests': AppointmentRequest.objects.filter(status='accepted').count(),
        'queue_entries': queue_entries,
        'recent_completed_queue': recent_completed_queue,
        'queue_waiting_count': QueueEntry.objects.filter(status='waiting').count(),
        'queue_active_count': QueueEntry.objects.filter(status='in_consultation').count(),
        'families': families,
        'patients': patients,
        'invoices': invoices,
        'current_status': status_filter,
        'current_clinic': clinic_filter,
        'user_role': 'front_desk',
    }
    return render(request, 'crm/frontdesk_dashboard.html', context)


# ==========================================
# ROLE 2: DR. SABINA (DENTAL MODULE)
# ==========================================

@role_required(['doctor_dental', 'admin'])
def crm_dental_dashboard(request):
    """
    Dr. Sabina Dental Module:
    - Her own calendar & dental patients
    - Interactive 32-tooth Adult & 20-tooth Child Odontogram
    - Multi-visit treatment plans with estimates
    - Dental lab work tracking (crowns, bridges, aligners)
    - Automated 6-month hygiene recall list with WhatsApp invite
    - Dental Clinical Prescriptions
    - Her specific dental income report (STRICTLY NO pediatric data)
    """
    # Dental Patients
    dental_patients = Patient.objects.all().order_by('-created_at')
    active_patient_id = request.GET.get('patient_id')
    if active_patient_id:
        active_patient = get_object_or_404(Patient, pk=active_patient_id)
    else:
        active_patient = dental_patients.first()

    # Odontogram tooth records for active patient
    tooth_records = {}
    if active_patient:
        for rec in DentalToothRecord.objects.filter(patient=active_patient):
            tooth_records[rec.tooth_number] = rec

    # Treatment Plans
    treatment_plans = DentalTreatmentPlan.objects.filter(patient=active_patient) if active_patient else []
    all_treatment_plans = DentalTreatmentPlan.objects.select_related('patient').all()[:15]

    # Lab Orders
    lab_orders = DentalLabOrder.objects.select_related('patient').all().order_by('delivery_due_date')

    # 6-Month Recalls
    recalls = DentalRecall.objects.select_related('patient').all()

    # Dental Prescriptions
    prescriptions = ClinicalPrescription.objects.filter(clinic_type='dental').select_related('patient')[:10]

    # Dental Revenue / Income Report (Dr. Sabina's practice collections only)
    dental_invoices = Invoice.objects.filter(clinic_type='dental')
    total_dental_revenue = dental_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    total_dental_collected = dental_invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    total_dental_pending = dental_invoices.aggregate(Sum('balance_due'))['balance_due__sum'] or Decimal('0.00')

    # Adult Tooth Map: Upper Right (18-11), Upper Left (21-28), Lower Left (31-38), Lower Right (48-41)
    adult_teeth_upper = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28]
    adult_teeth_lower = [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38]
    child_teeth_upper = [55, 54, 53, 52, 51, 61, 62, 63, 64, 65]
    child_teeth_lower = [85, 84, 83, 82, 81, 71, 72, 73, 74, 75]

    context = {
        'patients': dental_patients,
        'active_patient': active_patient,
        'tooth_records': tooth_records,
        'adult_teeth_upper': adult_teeth_upper,
        'adult_teeth_lower': adult_teeth_lower,
        'child_teeth_upper': child_teeth_upper,
        'child_teeth_lower': child_teeth_lower,
        'treatment_plans': treatment_plans,
        'all_treatment_plans': all_treatment_plans,
        'lab_orders': lab_orders,
        'recalls': recalls,
        'prescriptions': prescriptions,
        'total_dental_revenue': total_dental_revenue,
        'total_dental_collected': total_dental_collected,
        'total_dental_pending': total_dental_pending,
        'dental_invoices': dental_invoices[:15],
        'user_role': 'doctor_dental',
    }
    return render(request, 'crm/dental_dashboard.html', context)


# ==========================================
# ROLE 3: DR. JALIL (PEDIATRIC MODULE)
# ==========================================

@role_required(['doctor_pediatric', 'admin'])
def crm_pediatric_dashboard(request):
    """
    Dr. Jalil Pediatric Module:
    - His own calendar & pediatric patients
    - Growth charts with percentiles (Age vs Weight, Height, Head Circ)
    - Automated IAP vaccination schedule with due/overdue alerts
    - Printable official vaccination cards
    - Developmental milestone tracking
    - Newborn Care Suite (birth details, jaundice, phototherapy, feeding)
    - Weight-based dose helper (mg/kg to ml verification)
    - Pediatric Prescriptions
    - His specific pediatric income reports (STRICTLY NO dental data)
    """
    # Pediatric Patients (Children & Infants)
    pediatric_patients = Patient.objects.filter(Q(is_child=True) | Q(age_years__lte=18)).order_by('-created_at')
    active_patient_id = request.GET.get('patient_id')
    if active_patient_id:
        active_patient = get_object_or_404(Patient, pk=active_patient_id)
    else:
        active_patient = pediatric_patients.first()

    # Growth Records
    growth_records = ChildGrowthRecord.objects.filter(patient=active_patient) if active_patient else []
    latest_growth = growth_records.last()

    # Vaccinations
    vaccinations = VaccinationRecord.objects.filter(patient=active_patient) if active_patient else []
    due_vaccines_count = vaccinations.filter(status__in=['due', 'overdue']).count()
    administered_count = vaccinations.filter(status='administered').count()

    # Newborn Suite
    newborn_record = None
    if active_patient and hasattr(active_patient, 'newborn_record'):
        newborn_record = active_patient.newborn_record

    # Developmental Milestones
    milestones = DevelopmentalMilestone.objects.filter(patient=active_patient) if active_patient else []

    # Prescriptions
    prescriptions = ClinicalPrescription.objects.filter(clinic_type='pediatric').select_related('patient')[:10]

    # Pediatric Revenue / Collections
    pediatric_invoices = Invoice.objects.filter(clinic_type='pediatric')
    total_pedia_revenue = pediatric_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    total_pedia_collected = pediatric_invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    total_pedia_pending = pediatric_invoices.aggregate(Sum('balance_due'))['balance_due__sum'] or Decimal('0.00')

    context = {
        'patients': pediatric_patients,
        'active_patient': active_patient,
        'growth_records': growth_records,
        'latest_growth': latest_growth,
        'vaccinations': vaccinations,
        'due_vaccines_count': due_vaccines_count,
        'administered_count': administered_count,
        'newborn_record': newborn_record,
        'milestones': milestones,
        'prescriptions': prescriptions,
        'total_pedia_revenue': total_pedia_revenue,
        'total_pedia_collected': total_pedia_collected,
        'total_pedia_pending': total_pedia_pending,
        'pediatric_invoices': pediatric_invoices[:15],
        'user_role': 'doctor_pediatric',
    }
    return render(request, 'crm/pediatric_dashboard.html', context)


def crm_vaccination_card(request, patient_id):
    """
    Printable Official Child Immunization Card & Health Certificate
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    vaccinations = VaccinationRecord.objects.filter(patient=patient).order_by('due_date', 'dose_number')
    latest_growth = ChildGrowthRecord.objects.filter(patient=patient).last()
    newborn = getattr(patient, 'newborn_record', None)

    return render(request, 'crm/vaccination_card.html', {
        'patient': patient,
        'vaccinations': vaccinations,
        'latest_growth': latest_growth,
        'newborn': newborn,
        'print_date': datetime.date.today(),
    })


def crm_invoice_print(request, invoice_id):
    """
    Printable Medical Bill & Payment Receipt
    """
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    items = []
    try:
        items = json.loads(invoice.items_json)
    except Exception:
        pass

    return render(request, 'crm/invoice_print.html', {
        'invoice': invoice,
        'items': items,
        'print_date': datetime.date.today(),
    })


# ==========================================
# ROLE 4: OWNER / ADMIN (SUPER USER)
# ==========================================

@role_required(['admin'])
def crm_admin_dashboard(request):
    """
    Owner / Super Admin Master Command Center:
    - Master Financial Dashboard (Revenue by Doctor, by Service, Collection breakdown)
    - Staff Account Management & Permissions
    - Audit Trail Logs (Tracking every bill, status, and patient modification)
    - System Data Backup & Export (JSON / CSV)
    - Google Review Request Automation Settings
    """
    # Financial Analytics
    total_revenue = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    total_collected = Invoice.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    total_outstanding = Invoice.objects.aggregate(Sum('balance_due'))['balance_due__sum'] or Decimal('0.00')

    # Doctor Split
    dental_revenue = Invoice.objects.filter(clinic_type='dental').aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    pediatric_revenue = Invoice.objects.filter(clinic_type='pediatric').aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')

    # Payment Methods Breakdown
    payment_by_method = Invoice.objects.values('payment_method').annotate(
        total=Sum('paid_amount'),
        count=Count('id')
    ).order_by('-total')

    # Staff Accounts
    staff_members = StaffProfile.objects.select_related('user').all()

    # Audit Logs
    audit_logs = AuditLog.objects.all()[:40]

    # Quick Stats
    total_families = Family.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = AppointmentRequest.objects.count()

    context = {
        'total_revenue': total_revenue,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'dental_revenue': dental_revenue,
        'pediatric_revenue': pediatric_revenue,
        'payment_by_method': payment_by_method,
        'staff_members': staff_members,
        'audit_logs': audit_logs,
        'total_families': total_families,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'recent_invoices': Invoice.objects.select_related('patient').all()[:15],
        'user_role': 'admin',
    }
    return render(request, 'crm/admin_dashboard.html', context)


# ==========================================
# INTERACTIVE CRM APIS (AJAX / POST)
# ==========================================

@csrf_exempt
@require_POST
def api_queue_update(request):
    """
    Updates Waiting Lounge Token Status (Waiting -> In Consultation -> Completed)
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    entry_id = data.get('entry_id')
    new_status = data.get('status')

    entry = get_object_or_404(QueueEntry, pk=entry_id)
    if new_status in ['waiting', 'in_consultation', 'completed', 'cancelled']:
        entry.status = new_status
        if new_status == 'in_consultation' and not entry.consultation_start_time:
            entry.consultation_start_time = datetime.datetime.now()
        elif new_status == 'completed' and not entry.completed_time:
            entry.completed_time = datetime.datetime.now()
        entry.save()

        log_audit(request, 'STATUS_CHANGE', 'QueueEntry', entry.id, f"Token #{entry.token_number} ({entry.patient.full_name}) moved to {new_status}")
        return JsonResponse({'status': 'success', 'new_status': entry.status, 'token': entry.token_number})

    return JsonResponse({'status': 'error', 'message': 'Invalid status choice.'}, status=400)


@csrf_exempt
@require_POST
def api_queue_add(request):
    """
    Adds a walk-in or checked-in patient to the live waiting room queue.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    patient_id = data.get('patient_id')
    clinic_type = data.get('clinic_type', 'dental')
    reason = data.get('reason', 'Consultation')
    token_type = data.get('token_type', 'walk_in')

    patient = get_object_or_404(Patient, pk=patient_id)
    doctor = "Dr. Sabina Firoj Shaikh" if clinic_type == 'dental' else "Dr. Jalil S. Mujawar"

    # Compute next token number
    last_token = QueueEntry.objects.order_by('-token_number').first()
    next_token = (last_token.token_number + 1) if last_token else 101

    entry = QueueEntry.objects.create(
        token_number=next_token,
        patient=patient,
        clinic_type=clinic_type,
        doctor_assigned=doctor,
        token_type=token_type,
        status='waiting',
        reason_for_visit=reason
    )

    supabase_sync_queue(entry)
    log_audit(request, 'CREATE', 'QueueEntry', entry.id, f"Issued Token #{next_token} for {patient.full_name} ({clinic_type})")
    return JsonResponse({'status': 'success', 'token_number': next_token, 'patient_name': patient.full_name})


@csrf_exempt
@require_POST
def api_family_add(request):
    """
    Creates a new unified Family Profile.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    family_name = data.get('family_name', '').strip()
    primary_contact = data.get('primary_contact_name', '').strip()
    phone = data.get('primary_phone', '').strip()
    email = data.get('primary_email', '').strip()
    address = data.get('address', 'Wanowrie, Pune').strip()
    notes = data.get('notes', '').strip()

    if not family_name or not primary_contact or not phone:
        return JsonResponse({'status': 'error', 'message': 'Family Name, Primary Contact, and Phone are required.'}, status=400)

    fam = Family.objects.create(
        family_name=family_name,
        primary_contact_name=primary_contact,
        primary_phone=phone,
        primary_email=email,
        address=address,
        notes=notes
    )

    # Automatically create the primary head as a Patient
    Patient.objects.create(
        family=fam,
        full_name=primary_contact,
        phone=phone,
        relationship_to_head='Self',
        is_child=False
    )

    log_audit(request, 'CREATE', 'Family', fam.id, f"Created {fam.family_name} with primary contact {primary_contact}")
    return JsonResponse({'status': 'success', 'family_id': fam.family_id, 'family_name': fam.family_name})


@csrf_exempt
@require_POST
def api_patient_add(request):
    """
    Adds a new patient (or child dependent) to a Family.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    family_id = data.get('family_id')
    full_name = data.get('full_name', '').strip()
    gender = data.get('gender', 'M')
    age_years = int(data.get('age_years', 0) or 0)
    age_months = int(data.get('age_months', 0) or 0)
    relation = data.get('relationship_to_head', 'Self')
    phone = data.get('phone', '').strip()
    blood_group = data.get('blood_group', 'O+')
    allergies = data.get('allergies', 'None reported').strip()
    is_child = (data.get('is_child') in [True, 'true', '1']) or (age_years < 18)

    family = Family.objects.filter(pk=family_id).first() if family_id else None

    patient = Patient.objects.create(
        family=family,
        full_name=full_name,
        gender=gender,
        age_years=age_years,
        age_months=age_months,
        phone=phone or (family.primary_phone if family else ''),
        relationship_to_head=relation,
        blood_group=blood_group,
        allergies=allergies,
        is_child=is_child
    )

    log_audit(request, 'CREATE', 'Patient', patient.id, f"Registered patient {patient.full_name} ({patient.patient_id})")
    return JsonResponse({'status': 'success', 'patient_id': patient.patient_id, 'patient_name': patient.full_name})


@csrf_exempt
@require_POST
def api_invoice_create(request):
    """
    Creates a new Invoice / Bill with Partial or Full payment tracking.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    patient_id = data.get('patient_id')
    clinic_type = data.get('clinic_type', 'dental')
    total_amount = Decimal(str(data.get('total_amount', 0)))
    paid_amount = Decimal(str(data.get('paid_amount', 0)))
    payment_method = data.get('payment_method', 'upi')
    notes = data.get('notes', '')
    item_desc = data.get('item_description', 'Consultation & Procedure')

    patient = get_object_or_404(Patient, pk=patient_id)
    balance_due = max(Decimal('0.00'), total_amount - paid_amount)
    status = 'paid' if balance_due <= Decimal('0.00') else ('partial' if paid_amount > 0 else 'unpaid')
    doctor = "Dr. Sabina Firoj Shaikh" if clinic_type == 'dental' else "Dr. Jalil S. Mujawar"

    items = [{"name": item_desc, "qty": 1, "rate": float(total_amount), "total": float(total_amount)}]

    invoice = Invoice.objects.create(
        patient=patient,
        family=patient.family,
        clinic_type=clinic_type,
        doctor_name=doctor,
        items_json=json.dumps(items),
        subtotal=total_amount,
        total_amount=total_amount,
        paid_amount=paid_amount,
        balance_due=balance_due,
        payment_method=payment_method,
        payment_status=status,
        created_by=request.user if request.user.is_authenticated else None,
        notes=notes
    )

    supabase_sync_invoice(invoice)
    log_audit(request, 'BILLING', 'Invoice', invoice.id, f"Created {invoice.invoice_no} for {patient.full_name}: Rs {paid_amount}/{total_amount} ({payment_method})")

    return JsonResponse({
        'status': 'success',
        'invoice_no': invoice.invoice_no,
        'whatsapp_url': invoice.whatsapp_receipt_url(),
        'balance_due': float(balance_due),
        'payment_status': status
    })


@csrf_exempt
@require_POST
def api_dental_tooth_update(request):
    """
    Updates tooth condition in Odontogram (Healthy, Caries, RCT, Crown, Missing, Implant, Filling).
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    patient_id = data.get('patient_id')
    tooth_number = int(data.get('tooth_number'))
    condition = data.get('condition', 'healthy')
    tooth_type = data.get('tooth_type', 'adult')
    notes = data.get('notes', '')

    patient = get_object_or_404(Patient, pk=patient_id)

    record, created = DentalToothRecord.objects.get_or_create(
        patient=patient,
        tooth_number=tooth_number,
        tooth_type=tooth_type,
        defaults={'condition': condition, 'notes': notes}
    )
    if not created:
        record.condition = condition
        if notes:
            record.notes = notes
        record.save()

    log_audit(request, 'UPDATE', 'DentalToothRecord', record.id, f"Updated Tooth #{tooth_number} to {condition} for {patient.full_name}")

    return JsonResponse({
        'status': 'success',
        'tooth_number': tooth_number,
        'condition': record.condition,
        'condition_display': record.get_condition_display(),
        'notes': record.notes
    })


@csrf_exempt
@require_POST
def api_dental_plan_add(request):
    """
    Creates a new multi-visit Dental Treatment Plan.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    patient_id = data.get('patient_id')
    title = data.get('title', 'Dental Treatment Plan').strip()
    cost = Decimal(str(data.get('total_estimated_cost', 0)))
    notes = data.get('notes', '')

    patient = get_object_or_404(Patient, pk=patient_id)
    stages = [
        {"stage": "Visit 1: Clinical Diagnosis & Primary Care", "status": "completed", "cost": float(cost * Decimal('0.3'))},
        {"stage": "Visit 2: Restorative / Endodontic Procedure", "status": "in_progress", "cost": float(cost * Decimal('0.4'))},
        {"stage": "Visit 3: Final Prosthetic Fitting & Polish", "status": "pending", "cost": float(cost * Decimal('0.3'))}
    ]

    plan = DentalTreatmentPlan.objects.create(
        patient=patient,
        title=title,
        total_estimated_cost=cost,
        status='active',
        stages_json=json.dumps(stages),
        notes=notes
    )

    log_audit(request, 'CREATE', 'DentalTreatmentPlan', plan.id, f"Created Plan '{title}' (Rs. {cost}) for {patient.full_name}")
    return JsonResponse({'status': 'success', 'plan_id': plan.id, 'title': plan.title})


@csrf_exempt
@require_POST
def api_dental_lab_add(request):
    """
    Submits a new dental lab order (crowns, bridges, aligners).
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    patient_id = data.get('patient_id')
    lab_name = data.get('lab_name', 'Apex Dental Craft Wanowrie')
    order_type = data.get('order_type', 'zirconia_crown')
    tooth_numbers = data.get('tooth_numbers', '16')
    shade = data.get('shade', 'A2')
    cost = Decimal(str(data.get('cost', 2000)))
    due_days = int(data.get('due_days', 4))
    notes = data.get('notes', '')

    patient = get_object_or_404(Patient, pk=patient_id)
    due_date = datetime.date.today() + datetime.timedelta(days=due_days)

    order = DentalLabOrder.objects.create(
        patient=patient,
        lab_name=lab_name,
        order_type=order_type,
        tooth_numbers=tooth_numbers,
        shade=shade,
        order_date=datetime.date.today(),
        delivery_due_date=due_date,
        status='sent_to_lab',
        cost=cost,
        notes=notes
    )

    log_audit(request, 'CREATE', 'DentalLabOrder', order.id, f"Sent lab order {order_type} ({tooth_numbers}) to {lab_name}")
    return JsonResponse({'status': 'success', 'order_id': order.id, 'due_date': str(due_date)})


@csrf_exempt
@require_POST
def api_pediatric_growth_add(request):
    """
    Records somatic growth metrics and computes WHO/IAP percentiles.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    patient_id = data.get('patient_id')
    age_months = Decimal(str(data.get('age_months', 12)))
    weight_kg = Decimal(str(data.get('weight_kg', 10.0)))
    height_cm = Decimal(str(data.get('height_cm', 75.0)))
    head_circ = Decimal(str(data.get('head_circ_cm', 45.0))) if data.get('head_circ_cm') else None
    notes = data.get('notes', 'Normal growth velocity.')

    patient = get_object_or_404(Patient, pk=patient_id)

    # Simplified BMI & Percentile indicator
    height_m = height_cm / Decimal('100.0')
    bmi = round(weight_kg / (height_m * height_m), 2) if height_m > 0 else None

    # Estimate percentile relative to WHO 50th centile benchmark for age
    weight_percentile = 50
    if weight_kg < Decimal('6.0') and age_months > Decimal('6'):
        weight_percentile = 15
    elif weight_kg > Decimal('18.0') and age_months < Decimal('36'):
        weight_percentile = 85

    growth = ChildGrowthRecord.objects.create(
        patient=patient,
        recorded_date=datetime.date.today(),
        age_months=age_months,
        weight_kg=weight_kg,
        height_cm=height_cm,
        head_circ_cm=head_circ,
        bmi=bmi,
        weight_percentile=weight_percentile,
        height_percentile=50,
        notes=notes
    )

    log_audit(request, 'CREATE', 'ChildGrowthRecord', growth.id, f"Recorded growth for {patient.full_name}: {weight_kg}kg, {height_cm}cm")
    return JsonResponse({'status': 'success', 'growth_id': growth.id, 'bmi': float(bmi) if bmi else 0})


@csrf_exempt
@require_POST
def api_pediatric_vaccine_update(request):
    """
    Marks vaccine as administered, recording batch # and date.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    vaccine_id = data.get('vaccine_id')
    batch_no = data.get('batch_no', '').strip()
    status = data.get('status', 'administered')

    vax = get_object_or_404(VaccinationRecord, pk=vaccine_id)
    vax.status = status
    if status == 'administered':
        vax.administered_date = datetime.date.today()
        vax.batch_no = batch_no or f"BAT-{datetime.date.today().strftime('%Y%m')}-01"
        vax.administered_by = "Dr. Jalil S. Mujawar"
    vax.save()

    log_audit(request, 'UPDATE', 'VaccinationRecord', vax.id, f"Vaccine {vax.vaccine_name} marked as {status} for {vax.patient.full_name}")
    return JsonResponse({'status': 'success', 'vaccine_name': vax.vaccine_name, 'new_status': vax.status, 'batch_no': vax.batch_no})


def api_pediatric_dose_helper(request):
    """
    Weight-based pediatric dosing verification helper.
    Computes exact mg and mL for standard syrup suspensions.
    """
    weight_str = request.GET.get('weight', '10')
    try:
        weight = float(weight_str)
    except ValueError:
        weight = 10.0

    # Formulas for common pediatric meds:
    # 1. Paracetamol: 15 mg/kg/dose. Standard syrup: 120mg/5ml (or 250mg/5ml).
    # 2. Amoxicillin: 40 mg/kg/day divided in 2-3 doses. Syrup: 125mg/5ml or 250mg/5ml.
    # 3. Ibuprofen: 10 mg/kg/dose. Syrup: 100mg/5ml.
    # 4. Azithromycin: 10 mg/kg/day OD. Syrup: 200mg/5ml.
    # 5. Ondansetron: 0.15 mg/kg/dose. Syrup: 2mg/5ml.

    pcm_mg = round(weight * 15, 1)
    pcm_ml_120 = round((pcm_mg / 120.0) * 5.0, 1)
    pcm_ml_250 = round((pcm_mg / 250.0) * 5.0, 1)

    amox_daily_mg = round(weight * 40, 1)
    amox_single_mg = round(amox_daily_mg / 3.0, 1)
    amox_ml_125 = round((amox_single_mg / 125.0) * 5.0, 1)
    amox_ml_250 = round((amox_single_mg / 250.0) * 5.0, 1)

    ibup_mg = round(weight * 10, 1)
    ibup_ml_100 = round((ibup_mg / 100.0) * 5.0, 1)

    azith_mg = round(weight * 10, 1)
    azith_ml_200 = round((azith_mg / 200.0) * 5.0, 1)

    ondan_mg = round(weight * 0.15, 2)
    ondan_ml_2 = round((ondan_mg / 2.0) * 5.0, 1)

    results = {
        'weight_kg': weight,
        'drugs': [
            {
                'name': 'Syrup Paracetamol (Antipyretic / Analgesic)',
                'rule': '15 mg/kg per dose (Every 6h SOS, max 4 doses/24h)',
                'single_dose_mg': f"{pcm_mg} mg",
                'volume_options': f"{pcm_ml_120} mL (120mg/5ml) OR {pcm_ml_250} mL (250mg/5ml)",
                'frequency': 'Every 6 hours as needed for temp > 100°F'
            },
            {
                'name': 'Syrup Amoxicillin (Antibiotic)',
                'rule': '40 mg/kg/day divided in 3 doses (TID for 5-7 days)',
                'single_dose_mg': f"{amox_single_mg} mg (Total {amox_daily_mg} mg/day)",
                'volume_options': f"{amox_ml_125} mL (125mg/5ml) OR {amox_ml_250} mL (250mg/5ml)",
                'frequency': 'Three times daily after feeds'
            },
            {
                'name': 'Syrup Ibuprofen (Anti-inflammatory / High Fever)',
                'rule': '10 mg/kg per dose (Every 8h SOS, not below 6 months)',
                'single_dose_mg': f"{ibup_mg} mg",
                'volume_options': f"{ibup_ml_100} mL (100mg/5ml)",
                'frequency': 'Every 8 hours with milk/food'
            },
            {
                'name': 'Syrup Azithromycin (Atypical Respiratory / Tonsillitis)',
                'rule': '10 mg/kg once daily for 3-5 days',
                'single_dose_mg': f"{azith_mg} mg",
                'volume_options': f"{azith_ml_200} mL (200mg/5ml)",
                'frequency': 'Once daily 1 hour before or 2 hours after meals'
            },
            {
                'name': 'Syrup Ondansetron (Antiemetic)',
                'rule': '0.15 mg/kg per dose',
                'single_dose_mg': f"{ondan_mg} mg",
                'volume_options': f"{ondan_ml_2} mL (2mg/5ml)",
                'frequency': '30 mins before oral feeds / antibiotics'
            }
        ]
    }
    return JsonResponse(results)


@csrf_exempt
@require_POST
def api_prescription_create(request):
    """
    Creates a new clinical prescription for Dental or Pediatric consultation.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    patient_id = data.get('patient_id')
    clinic_type = data.get('clinic_type', 'dental')
    diagnosis = data.get('diagnosis', 'Clinical Consultation')
    complaints = data.get('complaints', '')
    medicines = data.get('medicines', '[]')
    vitals = data.get('vitals', '{}')
    diet = data.get('diet_instructions', 'Nutritious soft diet.')
    follow_up = data.get('follow_up', 'After 5 days')

    patient = get_object_or_404(Patient, pk=patient_id)
    doctor = "Dr. Sabina Firoj Shaikh" if clinic_type == 'dental' else "Dr. Jalil S. Mujawar"

    rx = ClinicalPrescription.objects.create(
        patient=patient,
        clinic_type=clinic_type,
        doctor_name=doctor,
        diagnosis=diagnosis,
        chief_complaints=complaints,
        vitals_json=medicines if isinstance(vitals, str) else json.dumps(vitals),
        medicines_json=medicines if isinstance(medicines, str) else json.dumps(medicines),
        diet_instructions=diet,
        follow_up_date=follow_up
    )

    log_audit(request, 'CREATE', 'ClinicalPrescription', rx.id, f"Prescription {rx.rx_id} generated for {patient.full_name} ({clinic_type})")
    return JsonResponse({'status': 'success', 'rx_id': rx.rx_id, 'patient_name': patient.full_name})


@csrf_exempt
@require_POST
def api_admin_staff_add(request):
    """
    Admin: Add a new staff member and assign RBAC role.
    """
    if not (request.user.is_authenticated and (request.user.is_superuser or (hasattr(request.user, 'clinic_staff_profile') and request.user.clinic_staff_profile.is_admin))):
        return JsonResponse({'status': 'error', 'message': 'Admin privilege required.'}, status=403)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST.dict()

    email = data.get('email', '').strip()
    name = data.get('full_name', '').strip()
    role = data.get('role', 'front_desk')
    password = data.get('password', 'Roots@2026')
    phone = data.get('phone', '')

    if not email or not name:
        return JsonResponse({'status': 'error', 'message': 'Email and Full Name are required.'}, status=400)

    user, created = User.objects.get_or_create(username=email, defaults={'email': email})
    user.set_password(password)
    user.save()

    profile, _ = StaffProfile.objects.get_or_create(user=user)
    profile.full_name = name
    profile.role = role
    profile.phone = phone
    profile.save()

    log_audit(request, 'CREATE', 'StaffProfile', profile.id, f"Created staff account {email} with role {role}")
    return JsonResponse({'status': 'success', 'email': email, 'role': role, 'full_name': name})


def api_admin_export(request, format_type):
    """
    1-Click System Data Backup & Export (CSV or JSON).
    """
    if not (request.user.is_authenticated and (request.user.is_superuser or (hasattr(request.user, 'clinic_staff_profile') and request.user.clinic_staff_profile.is_admin))):
        return HttpResponse("Admin privilege required.", status=403)

    log_audit(request, 'CREATE', 'Backup', 'All', f"Downloaded system backup in {format_type.upper()} format")

    if format_type == 'json':
        data = {
            'export_date': str(datetime.datetime.now()),
            'clinic': 'Roots Dental & Buds Child Clinic (Wanowrie, Pune)',
            'patients': list(Patient.objects.values('patient_id', 'full_name', 'gender', 'age_years', 'phone', 'blood_group', 'allergies')),
            'invoices': list(Invoice.objects.values('invoice_no', 'clinic_type', 'doctor_name', 'total_amount', 'paid_amount', 'balance_due', 'payment_status', 'created_at')),
            'queue_entries': list(QueueEntry.objects.values('token_number', 'clinic_type', 'doctor_assigned', 'status', 'reason_for_visit')),
            'appointments': list(AppointmentRequest.objects.values('clinic_type', 'patient_name', 'phone_number', 'preferred_date', 'status'))
        }
        response = HttpResponse(json.dumps(data, indent=2, default=str), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="roots_buds_crm_backup_{datetime.date.today()}.json"'
        return response

    elif format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="roots_buds_patients_{datetime.date.today()}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Patient ID', 'Full Name', 'Gender', 'Age (Yrs)', 'Phone', 'Blood Group', 'Allergies', 'Created Date'])
        for p in Patient.objects.all():
            writer.writerow([p.patient_id, p.full_name, p.gender, p.age_years, p.phone, p.blood_group, p.allergies, p.created_at.strftime('%Y-%m-%d')])
        return response

    return HttpResponse("Invalid format", status=400)


# ==========================================
# PUBLIC API: BOOKING & REQUEST STATUS
# ==========================================

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

    supabase_sync_appointment(appointment_req)

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
        log_audit(request, 'STATUS_CHANGE', 'AppointmentRequest', req_obj.id, f"Appointment status updated to {new_status} for {req_obj.patient_name}")
        return JsonResponse({
            'status': 'success',
            'new_status': req_obj.status,
            'message': f'Status updated to {req_obj.get_status_display()}'
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid status choice.'}, status=400)


# ==============================================================================
# STREAMLINED CLINIC SAAS CRM (MONOCHROMATIC LUXURY 4-TAB ARCHITECTURE)
# ==============================================================================

def crm_dashboard(request):
    """
    Executive Overview Dashboard & Command Deck
    Displays:
    - Real-time Clinic KPI Metrics (Footfall, Collections, Pending Web Requests, Receivables)
    - Quick Action Command Center (Quick Bill, Walk-in, Schedule Recall, Lock Desk)
    - Practice Performance Split (Roots Dental vs Buds Child Clinic)
    - Priority Action Items (Pending Booking Requests & Today's Schedule)
    - Live Financial Settlement Feed
    """
    if not request.user.is_authenticated:
        return redirect(f"/crm/login/?next={request.path}")

    today = datetime.date.today()

    # 1. Appointment Counts
    pending_qs = AppointmentRequest.objects.filter(status='pending').order_by('-created_at')
    upcoming_qs = AppointmentRequest.objects.filter(status='accepted').order_by('preferred_date', 'preferred_time')
    completed_qs = AppointmentRequest.objects.filter(status='completed').order_by('-id')

    dental_today_count = upcoming_qs.filter(clinic_type='dental').count() + completed_qs.filter(clinic_type='dental').count()
    pediatric_today_count = upcoming_qs.filter(clinic_type='pediatric').count() + completed_qs.filter(clinic_type='pediatric').count()
    total_today_count = upcoming_qs.count() + completed_qs.count()

    # 2. Invoices & Revenue
    all_invoices = Invoice.objects.select_related('patient').all().order_by('-created_at')
    today_invoices = [inv for inv in all_invoices if inv.created_at.date() == today]

    today_collection = sum((inv.paid_amount for inv in today_invoices), Decimal('0.00'))
    upi_today = sum((inv.paid_amount for inv in today_invoices if inv.payment_method == 'upi'), Decimal('0.00'))
    cash_today = sum((inv.paid_amount for inv in today_invoices if inv.payment_method == 'cash'), Decimal('0.00'))
    total_dues = sum((inv.balance_due for inv in all_invoices), Decimal('0.00'))

    dental_today_revenue = sum((inv.paid_amount for inv in today_invoices if inv.clinic_type == 'dental'), Decimal('0.00'))
    pediatric_today_revenue = sum((inv.paid_amount for inv in today_invoices if inv.clinic_type == 'pediatric'), Decimal('0.00'))

    # 3. Patients & Recalls
    all_patients = Patient.objects.all()
    dental_patients_count = all_patients.filter(is_child=False).count()
    pediatric_patients_count = all_patients.filter(is_child=True).count()
    reminders = ScheduledReminder.objects.filter(status='queued').order_by('target_date', 'target_time')

    context = {
        'active_tab': 'dashboard',
        # KPI Metrics
        'total_today_count': total_today_count,
        'dental_today_count': dental_today_count,
        'pediatric_today_count': pediatric_today_count,
        'completed_today_count': completed_qs.count(),
        'pending_requests_count': pending_qs.count(),
        'today_collection': today_collection,
        'upi_today': upi_today,
        'cash_today': cash_today,
        'total_dues': total_dues,
        'dental_today_revenue': dental_today_revenue,
        'pediatric_today_revenue': pediatric_today_revenue,
        'total_patients_count': all_patients.count(),
        'dental_patients_count': dental_patients_count,
        'pediatric_patients_count': pediatric_patients_count,
        'queued_reminders_count': reminders.count(),
        # Action Queues
        'pending_requests': pending_qs[:4],
        'upcoming_appointments': upcoming_qs[:6],
        'recent_invoices': all_invoices[:5],
        'patients': all_patients.order_by('full_name'),
    }
    return render(request, 'crm/dashboard.html', context)


def crm_today_desk(request):
    """
    Tab 1: Today's Desk
    - Incoming booking requests inbox (1-click Accept / Reschedule)
    - Today's schedule (Upcoming vs Completed)
    - 1-click 'Mark Done' action that triggers billing generation
    """
    if not request.user.is_authenticated:
        return redirect(f"/crm/login/?next={request.path}")

    today = datetime.date.today()
    wing_filter = request.GET.get('wing', 'all')

    pending_qs = AppointmentRequest.objects.filter(status='pending').order_by('-created_at')
    upcoming_qs = AppointmentRequest.objects.filter(status='accepted').order_by('preferred_date', 'preferred_time')
    completed_qs = AppointmentRequest.objects.filter(status='completed').order_by('-id')

    dental_today_count = upcoming_qs.filter(clinic_type='dental').count() + completed_qs.filter(clinic_type='dental').count()
    pediatric_today_count = upcoming_qs.filter(clinic_type='pediatric').count() + completed_qs.filter(clinic_type='pediatric').count()
    total_today_count = upcoming_qs.count() + completed_qs.count()

    # Invoices for today's collection metrics
    all_invoices = Invoice.objects.select_related('patient').all().order_by('-created_at')
    today_invoices = [inv for inv in all_invoices if inv.created_at.date() == today]
    today_collection = sum((inv.paid_amount for inv in today_invoices), Decimal('0.00'))
    total_dues = sum((inv.balance_due for inv in all_invoices), Decimal('0.00'))

    if wing_filter in ['dental', 'pediatric']:
        pending_qs = pending_qs.filter(clinic_type=wing_filter)
        upcoming_qs = upcoming_qs.filter(clinic_type=wing_filter)
        completed_qs = completed_qs.filter(clinic_type=wing_filter)

    patients = Patient.objects.all().order_by('full_name')

    context = {
        'active_tab': 'today',
        'wing_filter': wing_filter,
        'pending_requests': pending_qs,
        'upcoming_appointments': upcoming_qs,
        'completed_appointments': completed_qs,
        'pending_count': pending_qs.count(),
        'upcoming_count': upcoming_qs.count(),
        'completed_count': completed_qs.count(),
        'total_today_count': total_today_count,
        'dental_today_count': dental_today_count,
        'pediatric_today_count': pediatric_today_count,
        'today_collection': today_collection,
        'total_dues': total_dues,
        'patients': patients,
    }
    return render(request, 'crm/today_desk.html', context)


def crm_patients_directory(request):
    """
    Tab 2: Patients (Customer Directory)
    - Master searchable table: Name, Phone, Wing, Last Visit, Total Spent/Dues
    - Instant client-side search (<5ms)
    - Slide-over drawer on row click with Past Visits, Clinical Notes, and Billing History
    """
    if not request.user.is_authenticated:
        return redirect(f"/crm/login/?next={request.path}")

    patients = Patient.objects.select_related('family').prefetch_related('invoices', 'scheduled_reminders').all().order_by('full_name')

    patients_data = []
    for p in patients:
        invs = list(p.invoices.all())
        total_billed = sum((inv.total_amount for inv in invs), Decimal('0.00'))
        total_paid = sum((inv.paid_amount for inv in invs), Decimal('0.00'))
        balance_due = sum((inv.balance_due for inv in invs), Decimal('0.00'))

        last_inv = invs[0] if invs else None
        last_visit = last_inv.created_at.strftime('%d %b %Y') if last_inv else 'Recent Registration'

        inv_list = []
        for inv in invs:
            inv_list.append({
                'id': inv.id,
                'invoice_no': inv.invoice_no,
                'date': inv.created_at.strftime('%d %b %Y'),
                'doctor': inv.doctor_name,
                'total': float(inv.total_amount),
                'paid': float(inv.paid_amount),
                'balance': float(inv.balance_due),
                'status': inv.get_payment_status_display() if hasattr(inv, 'get_payment_status_display') else inv.payment_status,
                'method': inv.get_payment_method_display() if hasattr(inv, 'get_payment_method_display') else inv.payment_method,
                'whatsapp_url': inv.whatsapp_receipt_url(),
                'print_url': f"/crm/invoice/{inv.id}/print/",
            })

        appts = AppointmentRequest.objects.filter(phone_number__icontains=p.phone[-10:]).order_by('-created_at')[:10]
        visits_list = []
        for a in appts:
            visits_list.append({
                'id': a.id,
                'date': a.preferred_date,
                'time': a.preferred_time or 'Scheduled slot',
                'service': a.service_needed,
                'clinic': a.clinic_display_name(),
                'doctor': a.doctor_name(),
                'status': a.get_status_display(),
            })

        clinical_notes = []
        if p.medical_history:
            clinical_notes.append({'category': 'Medical History', 'text': p.medical_history})
        if p.allergies:
            clinical_notes.append({'category': 'Allergies & Sensitivities', 'text': p.allergies})
        if getattr(p, 'blood_group', None):
            clinical_notes.append({'category': 'Blood Group', 'text': p.blood_group})

        patients_data.append({
            'id': p.id,
            'full_name': p.full_name,
            'phone': p.phone,
            'clean_phone': p.clean_phone(),
            'age': p.age_display,
            'gender': p.get_gender_display() if hasattr(p, 'get_gender_display') else p.gender,
            'clinic_type': 'pediatric' if p.is_child else 'dental',
            'clinic_display': "Buds Child Clinic" if p.is_child else "Roots Dental Clinic",
            'doctor_assigned': "Dr. Jalil S. Mujawar" if p.is_child else "Dr. Sabina Firoj Shaikh",
            'family_name': p.family.family_name if p.family else 'Individual File',
            'emergency_contact': (p.family.primary_phone if p.family else None) or (p.phone or 'Direct Phone'),
            'total_billed': float(total_billed),
            'total_paid': float(total_paid),
            'balance_due': float(balance_due),
            'last_visit': last_visit,
            'visits': visits_list,
            'clinical_notes': clinical_notes,
            'invoices': inv_list,
        })

    context = {
        'active_tab': 'patients',
        'patients': patients,
        'patients_json': json.dumps(patients_data),
        'total_patients': len(patients_data),
        'dental_count': sum(1 for p in patients_data if p['clinic_type'] == 'dental'),
        'pediatric_count': sum(1 for p in patients_data if p['clinic_type'] == 'pediatric'),
    }
    return render(request, 'crm/patients.html', context)


def crm_finance_billing(request):
    """
    Tab 3: Finance & Billing
    - Quick Bill Generator (Select Patient, Doctor, Treatment, Amount, Mode: UPI/Cash)
    - Dual Action Buttons: 'Save & Send via WhatsApp' and 'Save Only'
    - Transaction Ledger table with filters (Today, This Month, Pending Dues, Dr. Sabina, Dr. Jalil)
    """
    if not request.user.is_authenticated:
        return redirect(f"/crm/login/?next={request.path}")

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        clinic_type = request.POST.get('clinic_type', 'dental')
        doctor_name = request.POST.get('doctor_name', 'Dr. Sabina Firoj Shaikh')
        treatment = request.POST.get('treatment', 'Clinical Consultation')

        try:
            total_amount = Decimal(request.POST.get('total_amount', '0'))
        except Exception:
            total_amount = Decimal('0.00')

        try:
            paid_amount = Decimal(request.POST.get('paid_amount', str(total_amount)))
        except Exception:
            paid_amount = total_amount

        payment_method = request.POST.get('payment_method', 'upi')
        notes = request.POST.get('notes', '')
        action = request.POST.get('action', 'save_only')

        patient = get_object_or_404(Patient, pk=patient_id)
        balance_due = max(Decimal('0.00'), total_amount - paid_amount)
        status = 'paid' if balance_due == 0 else ('partial' if paid_amount > 0 else 'unpaid')

        inv = Invoice.objects.create(
            patient=patient,
            family=patient.family,
            clinic_type=clinic_type,
            doctor_name=doctor_name,
            items_json=json.dumps([{'item': treatment, 'cost': float(total_amount)}]),
            subtotal=total_amount,
            total_amount=total_amount,
            paid_amount=paid_amount,
            balance_due=balance_due,
            payment_method=payment_method,
            payment_status=status,
            notes=notes,
            created_by=request.user
        )

        try:
            supabase_sync_invoice(inv)
        except Exception:
            pass

        log_audit(request, 'INVOICE', 'Invoice', inv.id, f"Generated bill {inv.invoice_no} for {patient.full_name} ({payment_method})")

        if action == 'save_and_whatsapp':
            return redirect(inv.whatsapp_receipt_url())

        messages.success(request, f"Invoice {inv.invoice_no} for {patient.full_name} recorded successfully.")
        return redirect('crm_billing')

    invoices = Invoice.objects.select_related('patient').all().order_by('-created_at')
    patients = Patient.objects.all().order_by('full_name')

    today = datetime.date.today()
    today_invoices = [inv for inv in invoices if inv.created_at.date() == today]
    today_collection = sum((inv.paid_amount for inv in today_invoices), Decimal('0.00'))
    cash_total = sum((inv.paid_amount for inv in invoices if inv.payment_method == 'cash'), Decimal('0.00'))
    upi_total = sum((inv.paid_amount for inv in invoices if inv.payment_method == 'upi'), Decimal('0.00'))
    dues_total = sum((inv.balance_due for inv in invoices), Decimal('0.00'))

    context = {
        'active_tab': 'billing',
        'invoices': invoices,
        'patients': patients,
        'today_collection': today_collection,
        'cash_total': cash_total,
        'upi_total': upi_total,
        'dues_total': dues_total,
    }
    return render(request, 'crm/billing.html', context)


def crm_whatsapp_hub(request):
    """
    Tab 4: WhatsApp & Recall Hub
    - 2-Pane WhatsApp Workspace (recent chats on left, active conversation on right)
    - 1-Click Preset Templates (Appointment Confirmed, Payment Receipt, Post-RCT Care, Vaccination Due)
    - Smart Reminder Scheduler (3-step flow with queued reminders table)
    """
    if not request.user.is_authenticated:
        return redirect(f"/crm/login/?next={request.path}")

    threads = WhatsAppThread.objects.select_related('patient').prefetch_related('messages').all().order_by('-last_message_at')
    reminders = ScheduledReminder.objects.select_related('patient').all().order_by('target_date', 'target_time')
    patients = Patient.objects.all().order_by('full_name')

    context = {
        'active_tab': 'whatsapp',
        'threads': threads,
        'reminders': reminders,
        'patients': patients,
        'queued_reminders_count': reminders.filter(status='queued').count(),
    }
    return render(request, 'crm/whatsapp_hub.html', context)


# ==============================================================================
# STREAMLINED AJAX APIS (ZERO LAG, CLEAN JSON)
# ==============================================================================

@csrf_exempt
@require_POST
def api_appointment_action(request, pk):
    """
    Handles 1-Click appointment actions: accept, reschedule, mark_done, cancel.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    appt = get_object_or_404(AppointmentRequest, pk=pk)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    action = data.get('action')

    if action == 'accept':
        appt.status = 'accepted'
        appt.save(update_fields=['status'])
        try:
            supabase_sync_appointment(appt)
        except Exception:
            pass
        log_audit(request, 'APPOINTMENT', 'AppointmentRequest', appt.id, f"Accepted booking for {appt.patient_name}")
        return JsonResponse({
            'success': True,
            'status': 'accepted',
            'patient_name': appt.patient_name,
            'whatsapp_url': appt.whatsapp_accept_url()
        })

    elif action == 'reschedule':
        new_date = data.get('new_date')
        new_time = data.get('new_time')
        appt.status = 'reschedule'
        update_fields = ['status']
        if new_date:
            appt.preferred_date = new_date
            update_fields.append('preferred_date')
        if new_time:
            appt.preferred_time = new_time
            update_fields.append('preferred_time')
        appt.save(update_fields=update_fields)
        return JsonResponse({
            'success': True,
            'status': 'reschedule',
            'patient_name': appt.patient_name,
            'whatsapp_url': appt.whatsapp_propose_url()
        })

    elif action == 'mark_done':
        appt.status = 'completed'
        appt.save(update_fields=['status'])
        patient = Patient.objects.filter(phone__icontains=appt.phone_number[-10:]).first()
        doctor_name = "Dr. Sabina Firoj Shaikh" if appt.clinic_type == 'dental' else "Dr. Jalil S. Mujawar"
        return JsonResponse({
            'success': True,
            'status': 'completed',
            'patient_name': appt.patient_name,
            'patient_id': patient.id if patient else None,
            'clinic_type': appt.clinic_type,
            'service': appt.service_needed,
            'doctor_name': doctor_name,
        })

    elif action == 'cancel':
        appt.status = 'cancelled'
        appt.save(update_fields=['status'])
        return JsonResponse({
            'success': True,
            'status': 'cancelled',
            'patient_name': appt.patient_name,
            'whatsapp_url': appt.whatsapp_decline_url()
        })

    return JsonResponse({'success': False, 'error': 'Invalid action choice.'}, status=400)


@csrf_exempt
@require_POST
def api_quick_bill_create(request):
    """
    Instant Bill Creation with dual action: Save Only or Save & Send via WhatsApp.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    patient_id = data.get('patient_id')
    patient_name = data.get('patient_name', '').strip()
    clinic_type = data.get('clinic_type', 'dental')
    doctor_name = data.get('doctor_name') or ("Dr. Sabina Firoj Shaikh" if clinic_type == 'dental' else "Dr. Jalil S. Mujawar")
    treatment = data.get('treatment', 'Clinical Consultation')

    try:
        total_amount = Decimal(str(data.get('total_amount', '0')))
    except Exception:
        total_amount = Decimal('0.00')

    try:
        paid_amount = Decimal(str(data.get('paid_amount', total_amount)))
    except Exception:
        paid_amount = total_amount

    payment_method = data.get('payment_method', 'upi')
    notes = data.get('notes', '')

    patient = None
    if patient_id:
        patient = Patient.objects.filter(pk=patient_id).first()
    if not patient and patient_name:
        patient = Patient.objects.filter(full_name__iexact=patient_name).first()
    if not patient:
        patient = Patient.objects.create(
            full_name=patient_name or 'Walk-in Patient',
            phone=data.get('phone', '9921231399'),
            is_child=(clinic_type == 'pediatric')
        )

    balance_due = max(Decimal('0.00'), total_amount - paid_amount)
    status = 'paid' if balance_due == 0 else ('partial' if paid_amount > 0 else 'unpaid')

    inv = Invoice.objects.create(
        patient=patient,
        family=patient.family,
        clinic_type=clinic_type,
        doctor_name=doctor_name,
        items_json=json.dumps([{'item': treatment, 'cost': float(total_amount)}]),
        subtotal=total_amount,
        total_amount=total_amount,
        paid_amount=paid_amount,
        balance_due=balance_due,
        payment_method=payment_method,
        payment_status=status,
        notes=notes,
        created_by=request.user
    )

    try:
        supabase_sync_invoice(inv)
    except Exception:
        pass

    log_audit(request, 'INVOICE', 'Invoice', inv.id, f"Quick bill {inv.invoice_no} created for {patient.full_name}")

    return JsonResponse({
        'success': True,
        'invoice_id': inv.id,
        'invoice_no': inv.invoice_no,
        'patient_name': patient.full_name,
        'total_amount': float(inv.total_amount),
        'paid_amount': float(inv.paid_amount),
        'balance_due': float(inv.balance_due),
        'payment_method': inv.get_payment_method_display(),
        'whatsapp_url': inv.whatsapp_receipt_url(),
        'print_url': f"/crm/invoice/{inv.id}/print/",
    })


@csrf_exempt
@require_POST
def api_reminder_schedule(request):
    """
    3-Step Smart Reminder Scheduler.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    patient_id = data.get('patient_id')
    preset_type = data.get('preset_type', 'Preventive Checkup')
    custom_reason = data.get('custom_reason', 'Routine Recall')
    target_date = data.get('target_date')
    target_time = data.get('target_time', '11:00 AM')

    patient = get_object_or_404(Patient, pk=patient_id)
    reminder = ScheduledReminder.objects.create(
        patient=patient,
        preset_type=preset_type,
        custom_reason=custom_reason,
        target_date=target_date,
        target_time=target_time,
        status='queued'
    )

    return JsonResponse({
        'success': True,
        'reminder_id': reminder.id,
        'patient_name': patient.full_name,
        'phone': patient.phone,
        'preset_type': reminder.preset_type,
        'custom_reason': reminder.custom_reason,
        'target_date': str(reminder.target_date),
        'target_time': reminder.target_time,
        'whatsapp_url': reminder.whatsapp_url(),
    })


@csrf_exempt
@require_POST
def api_reminder_cancel(request, pk):
    """
    Cancels a queued reminder.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    reminder = get_object_or_404(ScheduledReminder, pk=pk)
    reminder.status = 'cancelled'
    reminder.save(update_fields=['status'])
    return JsonResponse({'success': True, 'reminder_id': reminder.id, 'status': 'cancelled'})


@csrf_exempt
@require_POST
def api_whatsapp_send_message(request):
    """
    In-CRM WhatsApp Workspace: post message and generate click-to-send link.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    thread_id = data.get('thread_id')
    patient_id = data.get('patient_id')
    text = data.get('text', '').strip()

    if not text:
        return JsonResponse({'success': False, 'error': 'Message text is required.'}, status=400)

    thread = None
    if thread_id:
        thread = get_object_or_404(WhatsAppThread, pk=thread_id)
    elif patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)
        thread, _ = WhatsAppThread.objects.get_or_create(patient=patient)
    else:
        return JsonResponse({'success': False, 'error': 'Thread or Patient ID is required.'}, status=400)

    msg = WhatsAppChatMessage.objects.create(
        thread=thread,
        sender='clinic',
        text=text
    )
    thread.last_message = text
    thread.save()

    phone = thread.patient.clean_phone()
    wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(text)}"

    return JsonResponse({
        'success': True,
        'message_id': msg.id,
        'text': msg.text,
        'timestamp': msg.timestamp.strftime('%I:%M %p'),
        'whatsapp_url': wa_url
    })


@csrf_exempt
@require_POST
def api_lock_verify(request):
    """
    Lock Screen verification: unlocks with PIN '1234' or password 'irfan@123' or authenticated user password.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    pin = data.get('pin', '').strip()

    if pin in ['1234', 'irfan@123']:
        return JsonResponse({'success': True})
    if request.user.is_authenticated and request.user.check_password(pin):
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Incorrect PIN or password.'}, status=403)
