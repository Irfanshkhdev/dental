import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get('SUPABASE_URL') or os.environ.get('NEXT_PUBLIC_SUPABASE_URL') or 'https://mfzbsfgshicgtjitslho.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SECRET_KEY') or os.environ.get('SUPABASE_PUBLISHABLE_KEY') or os.environ.get('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY') or 'sb_publishable_8mJVkpQcqIkw3hProDURPw_4oGf_D-K'

_client: Client = None

def get_supabase():
    global _client
    if _client is None:
        try:
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Warning: Failed to initialize Supabase client: {e}")
            return None
    return _client


def supabase_sync_appointment(apt_obj):
    """
    Syncs an appointment request to Supabase in real-time.
    """
    client = get_supabase()
    if not client:
        return None
    try:
        data = {
            'id': apt_obj.id,
            'clinic_type': apt_obj.clinic_type,
            'patient_name': apt_obj.patient_name,
            'parent_name': apt_obj.parent_name or '',
            'phone_number': apt_obj.phone_number,
            'service_needed': apt_obj.service_needed,
            'preferred_date': apt_obj.preferred_date,
            'preferred_time': apt_obj.preferred_time or '',
            'notes': apt_obj.notes or '',
            'status': apt_obj.status,
        }
        res = client.from_('appointment_requests').upsert(data).execute()
        return res
    except Exception as e:
        print(f"Supabase appointment sync note: {e}")
        return None


def supabase_sync_queue(queue_obj):
    """
    Syncs a waiting lounge token to Supabase in real-time.
    """
    client = get_supabase()
    if not client:
        return None
    try:
        data = {
            'token_number': queue_obj.token_number,
            'patient_name': queue_obj.patient.full_name,
            'clinic_type': queue_obj.clinic_type,
            'doctor_assigned': queue_obj.doctor_assigned,
            'token_type': queue_obj.token_type,
            'status': queue_obj.status,
            'reason_for_visit': queue_obj.reason_for_visit,
        }
        res = client.from_('queue_entries').upsert(data).execute()
        return res
    except Exception as e:
        print(f"Supabase queue sync note: {e}")
        return None


def supabase_sync_invoice(invoice_obj):
    """
    Syncs an invoice to Supabase in real-time.
    """
    client = get_supabase()
    if not client:
        return None
    try:
        data = {
            'invoice_no': invoice_obj.invoice_no,
            'patient_name': invoice_obj.patient.full_name,
            'clinic_type': invoice_obj.clinic_type,
            'doctor_name': invoice_obj.doctor_name,
            'total_amount': float(invoice_obj.total_amount),
            'paid_amount': float(invoice_obj.paid_amount),
            'balance_due': float(invoice_obj.balance_due),
            'payment_method': invoice_obj.payment_method,
            'payment_status': invoice_obj.payment_status,
            'notes': invoice_obj.notes or '',
        }
        res = client.from_('invoices').upsert(data).execute()
        return res
    except Exception as e:
        print(f"Supabase invoice sync note: {e}")
        return None
