import json
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
import requests
from .models import Lead, Appointment, WorkflowLog


def trigger_crm_automation(event_name, contact_name, contact_email, contact_phone, payload_dict):
    """
    Routes lead/appointment/intake data to an external CRM Webhook (if configured in settings.CRM_WEBHOOK_URL)
    and logs the 3 automated workflow stages in Django ORM:
      1. Instant SMS & Email Confirmation
      2. 24-Hour Pre-Appointment Reminder
      3. Post-Visit Google Review Request
    """
    now = timezone.now()
    webhook_url = getattr(settings, 'CRM_WEBHOOK_URL', '')

    webhook_status = "Delivered (200 OK - Simulated)"
    if webhook_url:
        try:
            resp = requests.post(webhook_url, json=payload_dict, timeout=4)
            webhook_status = f"Delivered ({resp.status_code})"
        except Exception as exc:
            webhook_status = f"Queued for Retry ({str(exc)[:30]})"

    # 1. CRM API / Webhook Sync Log
    WorkflowLog.objects.create(
        event_type=event_name,
        recipient=f"{contact_name} ({contact_email})",
        channel="CRM API / Webhook",
        workflow_step="Inbound CRM Pipeline Sync",
        payload_preview=json.dumps(payload_dict),
        status=webhook_status,
        scheduled_for="Immediate (Real-time)"
    )

    # 2. Automated Workflow Step 1: Instant SMS + Email Confirmation
    WorkflowLog.objects.create(
        event_type=event_name,
        recipient=f"{contact_phone} | {contact_email}",
        channel="Twilio SMS + SendGrid Email",
        workflow_step="Step 1: Instant Confirmation",
        payload_preview=f"Hi {contact_name}, welcome to Aura Dental Spa! Your {event_name.lower()} is confirmed. Reply C to confirm or R to reschedule.",
        status="Sent Immediately",
        scheduled_for=now.strftime("%Y-%m-%d %H:%M UTC")
    )

    # 3. Automated Workflow Step 2: 24-Hour Pre-Visit Reminder
    reminder_time = (now + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M UTC (T-24h)")
    WorkflowLog.objects.create(
        event_type=event_name,
        recipient=contact_phone,
        channel="Automated SMS",
        workflow_step="Step 2: 24-Hour Reminder",
        payload_preview=f"Reminder: {contact_name}, we look forward to seeing you tomorrow at Aura Dental Spa. Digital intake forms: https://auradental.spa/patient-portal",
        status="Scheduled in Queue",
        scheduled_for=reminder_time
    )

    # 4. Automated Workflow Step 3: Post-Visit Review Request
    review_time = (now + timedelta(hours=52)).strftime("%Y-%m-%d %H:%M UTC (Post-Visit +2h)")
    WorkflowLog.objects.create(
        event_type=event_name,
        recipient=f"{contact_email} | {contact_phone}",
        channel="SMS + Email Drip",
        workflow_step="Step 3: Post-Visit Review Request",
        payload_preview=f"Thank you for visiting Aura Dental Spa, {contact_name}! How was your spa dental experience? Leave a 1-click Google Review: https://g.page/auradental/review",
        status="Scheduled in Queue",
        scheduled_for=review_time
    )


def ensure_seed_data():
    if not Lead.objects.exists():
        Lead.objects.create(
            full_name="Sophia Montgomery",
            email="sophia.m@example.com",
            phone="(310) 555-0192",
            service_interest="Porcelain Veneers & Digital Smile Design",
            pain_level="None / Cosmetic Inquiry",
            insurance_provider="Delta Dental PPO Premier",
            preferred_contact="SMS & Email",
            notes="Looking for 8 upper veneers before wedding in November.",
            source_page="Cosmetic Dentistry Page"
        )
        appt = Appointment.objects.create(
            patient_name="Alexander Wright",
            email="alex.wright@example.com",
            phone="(310) 555-0148",
            service_type="Invisalign® 3D Scan & Consultation",
            doctor="Dr. Elena Rostova, DDS",
            appointment_date="2026-10-29",
            appointment_time="10:30 AM",
            is_new_patient=True,
            insurance="Cigna Dental PPO"
        )
        trigger_crm_automation(
            "Smart Calendar Booking",
            appt.patient_name,
            appt.email,
            appt.phone,
            {"event": "SEED_BOOKING", "booking_ref": appt.booking_ref}
        )
