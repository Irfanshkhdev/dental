-- ==============================================================================
-- ROOTS DENTAL & BUDS CHILD CLINIC — SUPABASE DATABASE SCHEMA
-- ==============================================================================

-- 1. Appointment Requests Table
CREATE TABLE IF NOT EXISTS public.appointment_requests (
    id BIGSERIAL PRIMARY KEY,
    clinic_type VARCHAR(20) DEFAULT 'dental',
    patient_name VARCHAR(120) NOT NULL,
    parent_name VARCHAR(120) DEFAULT '',
    phone_number VARCHAR(30) NOT NULL,
    service_needed VARCHAR(120) DEFAULT 'General Consultation',
    preferred_date VARCHAR(50) NOT NULL,
    preferred_time VARCHAR(50) DEFAULT 'Morning (10:00 AM - 1:00 PM)',
    notes TEXT DEFAULT '',
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Waiting Lounge Queue Table
CREATE TABLE IF NOT EXISTS public.queue_entries (
    id BIGSERIAL PRIMARY KEY,
    token_number INT NOT NULL,
    patient_name VARCHAR(120) NOT NULL,
    clinic_type VARCHAR(20) DEFAULT 'dental',
    doctor_assigned VARCHAR(120) NOT NULL,
    token_type VARCHAR(20) DEFAULT 'walk_in',
    status VARCHAR(20) DEFAULT 'waiting',
    reason_for_visit VARCHAR(150) DEFAULT 'Consultation',
    check_in_time TIMESTAMPTZ DEFAULT NOW(),
    completed_time TIMESTAMPTZ
);

-- 3. Invoices & Billing Table
CREATE TABLE IF NOT EXISTS public.invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_no VARCHAR(32) UNIQUE NOT NULL,
    patient_name VARCHAR(120) NOT NULL,
    clinic_type VARCHAR(20) DEFAULT 'dental',
    doctor_name VARCHAR(120) NOT NULL,
    total_amount NUMERIC(10, 2) DEFAULT 0.00,
    paid_amount NUMERIC(10, 2) DEFAULT 0.00,
    balance_due NUMERIC(10, 2) DEFAULT 0.00,
    payment_method VARCHAR(20) DEFAULT 'upi',
    payment_status VARCHAR(20) DEFAULT 'paid',
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Patients Registry
CREATE TABLE IF NOT EXISTS public.patients (
    id BIGSERIAL PRIMARY KEY,
    patient_id VARCHAR(32) UNIQUE NOT NULL,
    family_name VARCHAR(120) DEFAULT '',
    full_name VARCHAR(120) NOT NULL,
    gender VARCHAR(10) DEFAULT 'M',
    age_years INT DEFAULT 0,
    phone VARCHAR(30) DEFAULT '',
    relationship_to_head VARCHAR(50) DEFAULT 'Self',
    blood_group VARCHAR(10) DEFAULT 'O+',
    allergies VARCHAR(255) DEFAULT 'None reported',
    is_child BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Audit Trail Logs
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_email VARCHAR(120) NOT NULL,
    action_type VARCHAR(30) DEFAULT 'UPDATE',
    target_model VARCHAR(60) NOT NULL,
    target_id VARCHAR(60) NOT NULL,
    summary TEXT NOT NULL,
    ip_address VARCHAR(60) DEFAULT '127.0.0.1',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS) & Public Access Policies for Demo
ALTER TABLE public.appointment_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.queue_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read appointment_requests" ON public.appointment_requests FOR SELECT USING (true);
CREATE POLICY "Allow public insert appointment_requests" ON public.appointment_requests FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update appointment_requests" ON public.appointment_requests FOR UPDATE USING (true);

CREATE POLICY "Allow public read queue_entries" ON public.queue_entries FOR SELECT USING (true);
CREATE POLICY "Allow public insert queue_entries" ON public.queue_entries FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update queue_entries" ON public.queue_entries FOR UPDATE USING (true);

CREATE POLICY "Allow public read invoices" ON public.invoices FOR SELECT USING (true);
CREATE POLICY "Allow public insert invoices" ON public.invoices FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update invoices" ON public.invoices FOR UPDATE USING (true);

CREATE POLICY "Allow public read patients" ON public.patients FOR SELECT USING (true);
CREATE POLICY "Allow public insert patients" ON public.patients FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read audit_logs" ON public.audit_logs FOR SELECT USING (true);
CREATE POLICY "Allow public insert audit_logs" ON public.audit_logs FOR INSERT WITH CHECK (true);
