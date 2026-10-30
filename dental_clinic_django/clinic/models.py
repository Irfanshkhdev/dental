import uuid
import urllib.parse
from django.db import models
from django.contrib.auth.models import User


def generate_lead_crm_id():
    return f"CRM-LD-{uuid.uuid4().hex[:8].upper()}"


def generate_booking_ref():
    return f"APT-{uuid.uuid4().hex[:6].upper()}"


def generate_intake_ref():
    return f"INT-{uuid.uuid4().hex[:6].upper()}"


def generate_family_id():
    return f"FAM-{uuid.uuid4().hex[:6].upper()}"


def generate_patient_id():
    return f"PAT-{uuid.uuid4().hex[:6].upper()}"


def generate_invoice_no():
    return f"INV-{uuid.uuid4().hex[:6].upper()}"


def generate_rx_id():
    return f"RX-{uuid.uuid4().hex[:6].upper()}"


# ==========================================
# 1. CORE AUTHENTICATION & RBAC PROFILE
# ==========================================

class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Owner / Super Admin'),
        ('front_desk', 'Front Desk (The Hub)'),
        ('doctor_dental', 'Dr. Sabina (Dental Module)'),
        ('doctor_pediatric', 'Dr. Jalil (Pediatric Module)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='clinic_staff_profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='front_desk')
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True, default='')
    qualification = models.CharField(max_length=150, blank=True, default='')
    specialty = models.CharField(max_length=150, blank=True, default='')
    avatar_color = models.CharField(max_length=30, default='bg-indigo-600')

    def __str__(self):
        return f"{self.full_name} [{self.get_role_display()}]"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser

    @property
    def is_front_desk(self):
        return self.role == 'front_desk'

    @property
    def is_dental(self):
        return self.role in ['doctor_dental', 'admin']

    @property
    def is_pediatric(self):
        return self.role in ['doctor_pediatric', 'admin']

    @property
    def can_view_financials(self):
        """Front desk strictly cannot see financial reports or doctor revenue."""
        return self.role in ['admin', 'doctor_dental', 'doctor_pediatric']

    @property
    def can_view_clinical(self):
        """Front desk strictly cannot see medical clinical notes."""
        return self.role in ['admin', 'doctor_dental', 'doctor_pediatric']


# ==========================================
# 2. FAMILY & PATIENT DIRECTORY
# ==========================================

class Family(models.Model):
    family_id = models.CharField(max_length=32, unique=True, default=generate_family_id)
    family_name = models.CharField(max_length=120)  # e.g., "Kulkarni Family"
    primary_contact_name = models.CharField(max_length=120)
    primary_phone = models.CharField(max_length=30)
    primary_email = models.CharField(max_length=120, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='Wanowrie, Pune')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.family_name} ({self.primary_phone})"

    @property
    def member_count(self):
        return self.members.count()


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    RELATION_CHOICES = [
        ('Self', 'Primary / Self'),
        ('Child', 'Child / Dependent'),
        ('Spouse', 'Spouse'),
        ('Parent', 'Parent / Senior'),
        ('Other', 'Other Relative'),
    ]

    patient_id = models.CharField(max_length=32, unique=True, default=generate_patient_id)
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    full_name = models.CharField(max_length=120)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='M')
    dob = models.DateField(null=True, blank=True)
    age_years = models.IntegerField(default=0)
    age_months = models.IntegerField(default=0)
    phone = models.CharField(max_length=30, blank=True, default='')
    relationship_to_head = models.CharField(max_length=50, choices=RELATION_CHOICES, default='Self')
    blood_group = models.CharField(max_length=10, blank=True, default='O+')
    allergies = models.CharField(max_length=255, blank=True, default='None reported')
    medical_history = models.TextField(blank=True, default='No significant systemic illness.')
    is_child = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.patient_id})"

    @property
    def age_display(self):
        if self.age_years > 0:
            return f"{self.age_years} yrs"
        elif self.age_months > 0:
            return f"{self.age_months} mos"
        return "Infant"

    def clean_phone(self):
        digits = ''.join(c for c in self.phone if c.isdigit())
        if len(digits) == 10:
            return f"91{digits}"
        elif digits.startswith('91') and len(digits) == 12:
            return digits
        return digits or '919921231399'


# ==========================================
# 3. LIVE WAITING ROOM & QUEUE ENGINE
# ==========================================

class QueueEntry(models.Model):
    CLINIC_CHOICES = [
        ('dental', 'Roots Dental Clinic'),
        ('pediatric', 'Buds Child Clinic'),
    ]
    STATUS_CHOICES = [
        ('waiting', 'In Waiting Lounge'),
        ('in_consultation', 'In Consultation'),
        ('completed', 'Consultation Completed'),
        ('cancelled', 'Cancelled / Left'),
    ]
    TOKEN_CHOICES = [
        ('walk_in', 'Walk-in'),
        ('appointment', 'Scheduled Appointment'),
    ]

    token_number = models.IntegerField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='queue_visits')
    clinic_type = models.CharField(max_length=20, choices=CLINIC_CHOICES, default='dental')
    doctor_assigned = models.CharField(max_length=120)
    token_type = models.CharField(max_length=20, choices=TOKEN_CHOICES, default='walk_in')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    reason_for_visit = models.CharField(max_length=150, default='Routine Checkup')
    check_in_time = models.DateTimeField(auto_now_add=True)
    consultation_start_time = models.DateTimeField(null=True, blank=True)
    completed_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['status', 'token_number']

    def __str__(self):
        return f"Token #{self.token_number} - {self.patient.full_name} ({self.status})"


# ==========================================
# 4. BILLING & INVOICING ENGINE
# ==========================================

class Invoice(models.Model):
    CLINIC_CHOICES = [
        ('dental', 'Roots Dental Clinic'),
        ('pediatric', 'Buds Child Clinic'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI / GPay / PhonePe'),
        ('card', 'Credit / Debit Card'),
        ('partial', 'Split / Partial Payment'),
    ]
    STATUS_CHOICES = [
        ('paid', 'Fully Paid'),
        ('partial', 'Partially Paid'),
        ('unpaid', 'Unpaid / Due'),
    ]

    invoice_no = models.CharField(max_length=32, unique=True, default=generate_invoice_no)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, related_name='family_invoices')
    clinic_type = models.CharField(max_length=20, choices=CLINIC_CHOICES, default='dental')
    doctor_name = models.CharField(max_length=120)
    items_json = models.TextField(default='[]')  # [{"item": "Root Canal 1st Visit", "cost": 3500}]
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='upi')
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='paid')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_no} - {self.patient.full_name} (Rs. {self.total_amount})"

    def whatsapp_receipt_url(self):
        phone = self.patient.clean_phone()
        clinic = "Roots Dental Clinic" if self.clinic_type == 'dental' else "Buds Child Clinic"
        msg = (
            f"Dear {self.patient.full_name}, thank you for visiting {clinic} (Wanowrie, Pune).\n"
            f"Receipt No: {self.invoice_no}\n"
            f"Doctor: {self.doctor_name}\n"
            f"Total: Rs. {self.total_amount}\n"
            f"Paid: Rs. {self.paid_amount}\n"
            f"Balance Due: Rs. {self.balance_due}\n"
            f"Payment Mode: {self.get_payment_method_display()}\n\n"
            f"Wishing you vibrant health! Helpline: +91 99212 31399."
        )
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"


# ==========================================
# 5. DENTAL MODULE (DR. SABINA)
# ==========================================

class DentalToothRecord(models.Model):
    TOOTH_TYPE_CHOICES = [
        ('adult', 'Adult Permanent (1-32)'),
        ('child', 'Child Primary (A-T / 51-85)'),
    ]
    CONDITION_CHOICES = [
        ('healthy', 'Healthy / Sound'),
        ('caries', 'Cavity / Caries'),
        ('rct', 'Root Canal Treated'),
        ('crown', 'Crown / Cap'),
        ('missing', 'Missing / Extracted'),
        ('implant', 'Implant'),
        ('filling', 'Composite Restoration'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tooth_records')
    tooth_number = models.IntegerField()  # Universal 1-32 or FDI notation
    tooth_type = models.CharField(max_length=10, choices=TOOTH_TYPE_CHOICES, default='adult')
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, default='healthy')
    surface = models.CharField(max_length=50, blank=True, default='')  # Occlusal, Mesial, Distal, etc.
    notes = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('patient', 'tooth_number', 'tooth_type')
        ordering = ['tooth_number']

    def __str__(self):
        return f"Tooth #{self.tooth_number} ({self.get_condition_display()}) - {self.patient.full_name}"


class DentalTreatmentPlan(models.Model):
    STATUS_CHOICES = [
        ('proposed', 'Proposed to Patient'),
        ('active', 'Active In-Progress'),
        ('completed', 'Treatment Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dental_treatment_plans')
    title = models.CharField(max_length=150)  # e.g., "Full Mouth Rehabilitation" or "Molar RCT & Zirconia Crown"
    total_estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    stages_json = models.TextField(default='[]')  # [{"stage": "Access opening & cleaning", "status": "done", "cost": 2500}]
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.patient.full_name} ({self.status})"


class DentalLabOrder(models.Model):
    ORDER_TYPE_CHOICES = [
        ('zirconia_crown', 'Zirconia Monolithic Crown'),
        ('pfm_crown', 'PFM Ceramic Crown'),
        ('clear_aligners', 'Clear Aligner Tray Set'),
        ('bridge', '3-Unit Ceramic Bridge'),
        ('denture', 'Cast Partial / Complete Denture'),
        ('night_guard', 'Dual Laminate Night Guard'),
    ]
    STATUS_CHOICES = [
        ('sent_to_lab', 'Sent to Lab'),
        ('in_fabrication', 'In Fabrication'),
        ('received', 'Received at Clinic'),
        ('fitted', 'Fitted to Patient'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dental_lab_orders')
    lab_name = models.CharField(max_length=120, default='Apex Dental Craft Wanowrie')
    order_type = models.CharField(max_length=40, choices=ORDER_TYPE_CHOICES, default='zirconia_crown')
    tooth_numbers = models.CharField(max_length=50)  # e.g., "16, 26"
    shade = models.CharField(max_length=20, default='A2')  # VITA Shade
    order_date = models.DateField()
    delivery_due_date = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='sent_to_lab')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-delivery_due_date']

    def __str__(self):
        return f"{self.get_order_type_display()} ({self.tooth_numbers}) - {self.patient.full_name}"


class DentalRecall(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Recall'),
        ('reminded', 'WhatsApp Reminder Sent'),
        ('scheduled', 'Appointment Scheduled'),
        ('completed', 'Recall Visit Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='recalls')
    recall_type = models.CharField(max_length=100, default='6-Month Routine Hygiene & Checkup')
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_reminded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.recall_type} - {self.patient.full_name} (Due: {self.due_date})"

    def whatsapp_recall_url(self):
        phone = self.patient.clean_phone()
        msg = (
            f"Dear {self.patient.full_name}, it has been 6 months since your last dental visit with Dr. Sabina Shaikh at Roots Dental Clinic. "
            f"Routine cleanings prevent hidden decay and protect your smile. Would you like to schedule your checkup this week? "
            f"Reply to book your preferred time. - Roots Dental, Wanowrie (+91 99212 31399)"
        )
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"


# ==========================================
# 6. PEDIATRIC MODULE (DR. JALIL)
# ==========================================

class ChildGrowthRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='growth_records')
    recorded_date = models.DateField()
    age_months = models.DecimalField(max_digits=5, decimal_places=1)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1)
    head_circ_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_percentile = models.IntegerField(default=50)  # 5, 25, 50, 75, 95
    height_percentile = models.IntegerField(default=50)
    notes = models.TextField(blank=True, default='Normal healthy growth along 50th centile.')

    class Meta:
        ordering = ['recorded_date']

    def __str__(self):
        return f"{self.patient.full_name} - {self.age_months}m ({self.weight_kg}kg, {self.height_cm}cm)"


class VaccinationRecord(models.Model):
    STATUS_CHOICES = [
        ('due', 'Due Soon'),
        ('overdue', 'Overdue'),
        ('administered', 'Administered'),
        ('exempt', 'Exempt / Postponed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=120)
    dose_number = models.IntegerField(default=1)
    recommended_age_str = models.CharField(max_length=60)  # e.g. "6 Weeks", "9 Months"
    due_date = models.DateField()
    administered_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='due')
    batch_no = models.CharField(max_length=60, blank=True, default='')
    manufacturer = models.CharField(max_length=120, blank=True, default='Serum Institute / GSK')
    administered_by = models.CharField(max_length=120, blank=True, default='Dr. Jalil S. Mujawar')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['due_date', 'dose_number']

    def __str__(self):
        return f"{self.vaccine_name} (Dose {self.dose_number}) - {self.patient.full_name} [{self.status}]"


class NewbornRecord(models.Model):
    DELIVERY_CHOICES = [
        ('normal', 'Full Term Normal Vaginal Delivery'),
        ('cesarean', 'Elective / Emergency LSCS'),
        ('assisted', 'Vacuum / Instrumental Assisted'),
    ]
    FEEDING_CHOICES = [
        ('ebf', 'Exclusive Breastfeeding (EBF)'),
        ('formula', 'Infant Formula'),
        ('mixed', 'Mixed Feeding (EBF + Formula)'),
    ]

    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='newborn_record')
    birth_date = models.DateField()
    birth_time = models.CharField(max_length=20, blank=True, default='10:30 AM')
    gestational_age_weeks = models.DecimalField(max_digits=4, decimal_places=1, default=39.0)
    birth_weight_kg = models.DecimalField(max_digits=4, decimal_places=2, default=3.10)
    birth_length_cm = models.DecimalField(max_digits=4, decimal_places=1, default=50.0)
    head_circumference_cm = models.DecimalField(max_digits=4, decimal_places=1, default=34.5)
    delivery_type = models.CharField(max_length=30, choices=DELIVERY_CHOICES, default='normal')
    apgar_1min = models.IntegerField(default=8)
    apgar_5min = models.IntegerField(default=9)
    blood_group = models.CharField(max_length=10, default='B+')
    maternal_history = models.CharField(max_length=200, blank=True, default='Uneventful antenatal period.')
    phototherapy_required = models.BooleanField(default=False)
    phototherapy_hours = models.IntegerField(default=0)
    peak_bilirubin_mg_dl = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    feeding_type = models.CharField(max_length=30, choices=FEEDING_CHOICES, default='ebf')
    pediatrician_notes = models.TextField(blank=True, default='Vigorous cry at birth, normal neonatal reflexes, pink and active.')

    def __str__(self):
        return f"Newborn Suite: {self.patient.full_name} ({self.gestational_age_weeks} wks, {self.birth_weight_kg} kg)"


class DevelopmentalMilestone(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='milestones')
    age_category = models.CharField(max_length=50)  # e.g., "6 Months", "12 Months"
    domain = models.CharField(max_length=50)  # Gross Motor, Fine Motor, Language, Social
    milestone_name = models.CharField(max_length=150)
    is_achieved = models.BooleanField(default=True)
    achieved_age_months = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True, default='On track for age')

    class Meta:
        ordering = ['age_category', 'domain']

    def __str__(self):
        return f"{self.milestone_name} - {self.patient.full_name} ({self.domain})"


# ==========================================
# 7. CLINICAL NOTES & PRESCRIPTIONS
# ==========================================

class ClinicalPrescription(models.Model):
    CLINIC_CHOICES = [
        ('dental', 'Roots Dental Clinic'),
        ('pediatric', 'Buds Child Clinic'),
    ]

    rx_id = models.CharField(max_length=32, unique=True, default=generate_rx_id)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    clinic_type = models.CharField(max_length=20, choices=CLINIC_CHOICES, default='dental')
    doctor_name = models.CharField(max_length=120)
    diagnosis = models.CharField(max_length=255)
    chief_complaints = models.TextField(blank=True, default='')
    vitals_json = models.TextField(default='{}')  # {"bp": "120/80", "pulse": "74", "temp": "98.6 F", "weight": "62 kg"}
    medicines_json = models.TextField(default='[]')  # [{"drug": "Amoxicillin 500mg", "freq": "1-0-1", "days": "5 days", "notes": "After food"}]
    diet_instructions = models.TextField(blank=True, default='Soft diet, plenty of fluids.')
    investigations_advised = models.TextField(blank=True, default='')
    follow_up_date = models.CharField(max_length=60, blank=True, default='After 5 days')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rx_id} - {self.patient.full_name} ({self.diagnosis})"


# ==========================================
# 8. AUDIT LOG ENGINE
# ==========================================

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created Record'),
        ('UPDATE', 'Modified Record'),
        ('DELETE', 'Deleted Record'),
        ('STATUS_CHANGE', 'Status Changed'),
        ('BILLING', 'Billing / Payment Recorded'),
        ('LOGIN', 'User Sign-in'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_email = models.CharField(max_length=120)
    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES, default='UPDATE')
    target_model = models.CharField(max_length=60)
    target_id = models.CharField(max_length=60)
    summary = models.TextField()
    ip_address = models.CharField(max_length=60, default='127.0.0.1')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.action_type}] {self.user_email} on {self.target_model}:{self.target_id}"


# ==========================================
# 9. EXISTING COMPATIBILITY MODELS (DO NOT BREAK)
# ==========================================

class AppointmentRequest(models.Model):
    CLINIC_CHOICES = [
        ('dental', 'Roots Dental Clinic'),
        ('pediatric', 'Buds Child Clinic'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('accepted', 'Accepted & Confirmed'),
        ('reschedule', 'Reschedule Proposed'),
        ('cancelled', 'Cancelled'),
    ]

    clinic_type = models.CharField(max_length=20, choices=CLINIC_CHOICES, default='dental')
    patient_name = models.CharField(max_length=120)
    parent_name = models.CharField(max_length=120, blank=True, null=True, default='')
    phone_number = models.CharField(max_length=30)
    service_needed = models.CharField(max_length=120, blank=True, default='General Consultation')
    preferred_date = models.CharField(max_length=50)
    preferred_time = models.CharField(max_length=50, blank=True, default='Morning (10:00 AM - 1:00 PM)')
    notes = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_clinic_type_display()}] {self.patient_name} - {self.phone_number} ({self.status})"

    def clean_phone(self):
        digits = ''.join(c for c in self.phone_number if c.isdigit())
        if len(digits) == 10:
            return f"91{digits}"
        elif digits.startswith('91') and len(digits) == 12:
            return digits
        return digits or '919921231399'

    def doctor_name(self):
        return "Dr. Sabina Firoj Shaikh (B.D.S, M.D.S Gold Medalist)" if self.clinic_type == 'dental' else "Dr. Jalil S. Mujawar (Senior Consultant Pediatrician & Neonatologist)"

    def clinic_display_name(self):
        return "Roots Dental Clinic" if self.clinic_type == 'dental' else "Buds Child Clinic"

    def whatsapp_accept_url(self):
        phone = self.clean_phone()
        clinic = self.clinic_display_name()
        name = self.patient_name
        date_str = self.preferred_date
        time_str = self.preferred_time or "11:00 AM"
        msg = f"Hello {name}, your appointment at {clinic} (Wanowrie, Pune) is confirmed for {date_str} at {time_str}. Please arrive 10 minutes early. - Front Desk, Roots & Buds (+91 99212 31399)"
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

    def whatsapp_decline_url(self):
        phone = self.clean_phone()
        clinic = self.clinic_display_name()
        name = self.patient_name
        msg = f"Hello {name}, we regret that our doctors are unavailable during your requested time for {clinic}. Please reply to reschedule or call us at +91 99212 31399. - Roots & Buds"
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

    def whatsapp_propose_url(self):
        phone = self.clean_phone()
        clinic = self.clinic_display_name()
        name = self.patient_name
        doc = "Dr. Sabina" if self.clinic_type == 'dental' else "Dr. Jalil"
        date_str = self.preferred_date
        msg = f"Hello {name}, {doc} is occupied during your requested slot for {clinic}. Could we schedule you for an alternative time on {date_str}? Please let us know what works best for you. - Roots & Buds (+91 99212 31399)"
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

    def whatsapp_reminder_url(self):
        phone = self.clean_phone()
        clinic = self.clinic_display_name()
        name = self.patient_name
        date_str = self.preferred_date
        time_str = self.preferred_time or "Scheduled time"
        msg = f"Friendly reminder for {name}: Your consultation at {clinic} (Wanowrie, Pune) is scheduled for {date_str} at {time_str}. Location: 108 One Place Commercial Spaces, Salunke Vihar Rd. See you soon!"
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"


class Lead(models.Model):
    crm_id = models.CharField(max_length=64, default=generate_lead_crm_id, unique=True)
    full_name = models.CharField(max_length=120)
    email = models.EmailField(max_length=120)
    phone = models.CharField(max_length=40)
    service_interest = models.CharField(max_length=80)
    pain_level = models.CharField(max_length=40, default="None / Routine")
    insurance_provider = models.CharField(max_length=80, default="Self-Pay / Unspecified")
    preferred_contact = models.CharField(max_length=40, default="SMS & Email")
    notes = models.TextField(blank=True, default="")
    source_page = models.CharField(max_length=80, default="Home")
    status = models.CharField(max_length=40, default="New Lead - Synced to CRM")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.crm_id})"


class Appointment(models.Model):
    booking_ref = models.CharField(max_length=64, default=generate_booking_ref, unique=True)
    patient_name = models.CharField(max_length=120)
    email = models.EmailField(max_length=120)
    phone = models.CharField(max_length=40)
    service_type = models.CharField(max_length=80)
    doctor = models.CharField(max_length=80)
    appointment_date = models.CharField(max_length=40)
    appointment_time = models.CharField(max_length=40)
    is_new_patient = models.BooleanField(default=True)
    insurance = models.CharField(max_length=80, default="Self-Pay / Insurance")
    crm_sync_status = models.CharField(max_length=60, default="Synced (Roots & Buds CRM)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_name} - {self.appointment_date} {self.appointment_time} ({self.booking_ref})"


class PatientIntake(models.Model):
    intake_ref = models.CharField(max_length=64, default=generate_intake_ref, unique=True)
    full_name = models.CharField(max_length=120)
    dob = models.CharField(max_length=40)
    email = models.EmailField(max_length=120)
    phone = models.CharField(max_length=40)
    insurance_provider = models.CharField(max_length=100)
    member_id = models.CharField(max_length=80)
    group_number = models.CharField(max_length=80, blank=True, default="")
    medical_conditions = models.TextField(blank=True, default="None reported")
    allergies = models.TextField(blank=True, default="None reported")
    dental_anxiety_level = models.CharField(max_length=80, default="Low - Relaxed")
    hipaa_consent = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.intake_ref})"


class WorkflowLog(models.Model):
    event_type = models.CharField(max_length=80)
    recipient = models.CharField(max_length=120)
    channel = models.CharField(max_length=40)
    workflow_step = models.CharField(max_length=120)
    payload_preview = models.TextField()
    status = models.CharField(max_length=40, default="Executed / Queued")
    scheduled_for = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.workflow_step} -> {self.recipient}"
