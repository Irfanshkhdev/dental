import uuid
import urllib.parse
from django.db import models


def generate_lead_crm_id():
    return f"CRM-LD-{uuid.uuid4().hex[:8].upper()}"


def generate_booking_ref():
    return f"APT-{uuid.uuid4().hex[:6].upper()}"


def generate_intake_ref():
    return f"INT-{uuid.uuid4().hex[:6].upper()}"


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
        return digits or '919876543210'

    def doctor_name(self):
        return "Dr. Sabina Firoj Shaikh (MDS Gold Medalist)" if self.clinic_type == 'dental' else "Dr. Jalil S. Mujawar (Senior Pediatrician)"

    def clinic_display_name(self):
        return "Roots Dental Clinic" if self.clinic_type == 'dental' else "Buds Child Clinic"

    def whatsapp_accept_url(self):
        phone = self.clean_phone()
        clinic = self.clinic_display_name()
        name = self.patient_name
        date_str = self.preferred_date
        time_str = self.preferred_time or "11:00 AM"
        msg = f"Hello {name}, your appointment at {clinic} (Wanowrie, Pune) is confirmed for {date_str} at {time_str}. Please arrive 10 minutes early. - Front Desk, Roots & Buds"
        return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

    def whatsapp_propose_url(self):
        phone = self.clean_phone()
        clinic = self.clinic_display_name()
        name = self.patient_name
        doc = "Dr. Sabina" if self.clinic_type == 'dental' else "Dr. Jalil"
        date_str = self.preferred_date
        msg = f"Hello {name}, {doc} is occupied during your requested slot for {clinic}. Could we schedule you for an alternative time on {date_str}? Please let us know what works best for you. - Roots & Buds"
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
