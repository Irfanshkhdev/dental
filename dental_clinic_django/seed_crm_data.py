import os
import django
import datetime
from decimal import Decimal
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aura_dental.settings')
django.setup()

from django.contrib.auth.models import User
from clinic.models import (
    StaffProfile, Family, Patient, QueueEntry, Invoice,
    DentalToothRecord, DentalTreatmentPlan, DentalLabOrder, DentalRecall,
    ChildGrowthRecord, VaccinationRecord, NewbornRecord, DevelopmentalMilestone,
    ClinicalPrescription, AuditLog, AppointmentRequest
)

def seed():
    print("🌱 Seeding Roots & Buds CRM Database...")

    # 1. Staff Accounts & RBAC Profiles
    users_data = [
        {
            'username': 'irfanshaikh3262@gmail.com',
            'email': 'irfanshaikh3262@gmail.com',
            'password': 'irfan@123',
            'full_name': 'Irfan Shaikh',
            'role': 'admin',
            'qualification': 'Clinic Owner & Executive Director',
            'specialty': 'Healthcare Operations & Management',
            'phone': '9921231399',
            'is_superuser': True,
            'is_staff': True,
            'avatar_color': 'bg-indigo-600',
        },
        {
            'username': 'sabina@rootsbuds.com',
            'email': 'sabina@rootsbuds.com',
            'password': 'sabina@123',
            'full_name': 'Dr. Sabina Firoj Shaikh',
            'role': 'doctor_dental',
            'qualification': 'B.D.S, M.D.S (Gold Medalist)',
            'specialty': 'Conservative Dentistry & Endodontics',
            'phone': '9921231399',
            'is_superuser': False,
            'is_staff': True,
            'avatar_color': 'bg-sky-600',
        },
        {
            'username': 'jalil@rootsbuds.com',
            'email': 'jalil@rootsbuds.com',
            'password': 'jalil@123',
            'full_name': 'Dr. Jalil S. Mujawar',
            'role': 'doctor_pediatric',
            'qualification': 'MBBS, DNB(Pediatrics), MNAMS, SCHP, PGPN, MBA-Hosp Admin',
            'specialty': 'Senior Consultant Pediatrician & Neonatologist',
            'phone': '9426914747',
            'is_superuser': False,
            'is_staff': True,
            'avatar_color': 'bg-emerald-600',
        },
        {
            'username': 'frontdesk@rootsbuds.com',
            'email': 'frontdesk@rootsbuds.com',
            'password': 'desk@123',
            'full_name': 'Ayesha Khan',
            'role': 'front_desk',
            'qualification': 'Head of Front Desk Operations',
            'specialty': 'Patient Concierge & Billing Hub',
            'phone': '02046010398',
            'is_superuser': False,
            'is_staff': False,
            'avatar_color': 'bg-rose-600',
        },
    ]

    for udata in users_data:
        user, created = User.objects.get_or_create(username=udata['username'])
        user.email = udata['email']
        user.set_password(udata['password'])
        user.is_superuser = udata['is_superuser']
        user.is_staff = udata['is_staff']
        user.save()

        profile, p_created = StaffProfile.objects.get_or_create(user=user)
        profile.role = udata['role']
        profile.full_name = udata['full_name']
        profile.qualification = udata['qualification']
        profile.specialty = udata['specialty']
        profile.phone = udata['phone']
        profile.avatar_color = udata['avatar_color']
        profile.save()
        print(f"  ✓ User {user.email} [{profile.role}] ready.")

    admin_user = User.objects.get(username='irfanshaikh3262@gmail.com')
    frontdesk_user = User.objects.get(username='frontdesk@rootsbuds.com')

    # 2. Families
    fam1, _ = Family.objects.get_or_create(
        family_name="Kulkarni Family",
        defaults={
            'primary_contact_name': 'Rahul Kulkarni',
            'primary_phone': '9822012345',
            'primary_email': 'rahul.kulkarni@example.com',
            'address': 'Flat 402, Green Acres, Salunke Vihar Rd, Wanowrie, Pune',
            'notes': 'Family under dental care with Dr. Sabina and pediatric care with Dr. Jalil.'
        }
    )

    fam2, _ = Family.objects.get_or_create(
        family_name="Deshmukh Family",
        defaults={
            'primary_contact_name': 'Amit Deshmukh',
            'primary_phone': '9890456789',
            'primary_email': 'amit.deshmukh@example.com',
            'address': 'B-301, Girme Heights, Wanowrie, Pune',
            'notes': 'Newborn baby born 2 months ago under Dr. Jalil.'
        }
    )

    fam3, _ = Family.objects.get_or_create(
        family_name="Mehta Family",
        defaults={
            'primary_contact_name': 'Sneha Mehta',
            'primary_phone': '9890123456',
            'primary_email': 'sneha.mehta@example.com',
            'address': 'Oxford Village, Wanowrie, Pune',
            'notes': 'Regular pediatric wellness visits.'
        }
    )

    # 3. Patients (Linking Adults and Children to Families)
    pat_rahul, _ = Patient.objects.get_or_create(
        full_name="Rahul Kulkarni",
        defaults={
            'family': fam1,
            'gender': 'M',
            'age_years': 38,
            'age_months': 0,
            'phone': '9822012345',
            'relationship_to_head': 'Self',
            'blood_group': 'B+',
            'allergies': 'Penicillin (mild rash)',
            'medical_history': 'Occasional acidity. Non-diabetic, Normotensive.',
            'is_child': False,
        }
    )

    pat_priyanka, _ = Patient.objects.get_or_create(
        full_name="Priyanka Kulkarni",
        defaults={
            'family': fam1,
            'gender': 'F',
            'age_years': 35,
            'age_months': 0,
            'phone': '9822012345',
            'relationship_to_head': 'Spouse',
            'blood_group': 'O+',
            'allergies': 'None reported',
            'medical_history': 'No systemic disease.',
            'is_child': False,
        }
    )

    pat_ananya, _ = Patient.objects.get_or_create(
        full_name="Ananya Kulkarni",
        defaults={
            'family': fam1,
            'gender': 'F',
            'dob': datetime.date(2022, 5, 14),
            'age_years': 4,
            'age_months': 5,
            'phone': '9822012345',
            'relationship_to_head': 'Child',
            'blood_group': 'B+',
            'allergies': 'None',
            'medical_history': 'Born at 39 weeks. No history of seizures or asthma.',
            'is_child': True,
        }
    )

    pat_kabir, _ = Patient.objects.get_or_create(
        full_name="Baby Kabir Deshmukh",
        defaults={
            'family': fam2,
            'gender': 'M',
            'dob': datetime.date(2026, 8, 25),
            'age_years': 0,
            'age_months': 2,
            'phone': '9890456789',
            'relationship_to_head': 'Child',
            'blood_group': 'O+',
            'allergies': 'None',
            'medical_history': 'Full term normal delivery. Robust neonatal vitals.',
            'is_child': True,
        }
    )

    pat_aarav, _ = Patient.objects.get_or_create(
        full_name="Aarav Mehta",
        defaults={
            'family': fam3,
            'gender': 'M',
            'dob': datetime.date(2022, 6, 10),
            'age_years': 4,
            'age_months': 4,
            'phone': '9890123456',
            'relationship_to_head': 'Child',
            'blood_group': 'A+',
            'allergies': 'None',
            'medical_history': 'Mild viral URTI last month, resolved.',
            'is_child': True,
        }
    )

    # 4. Live Queue Lounge Entries
    QueueEntry.objects.all().delete()
    q1 = QueueEntry.objects.create(
        token_number=101,
        patient=pat_rahul,
        clinic_type='dental',
        doctor_assigned='Dr. Sabina Firoj Shaikh',
        token_type='appointment',
        status='in_consultation',
        reason_for_visit='Root Canal Stage 2 - Obturation & Crown Prep (#16)',
        consultation_start_time=datetime.datetime.now() - datetime.timedelta(minutes=15)
    )

    q2 = QueueEntry.objects.create(
        token_number=102,
        patient=pat_kabir,
        clinic_type='pediatric',
        doctor_assigned='Dr. Jalil S. Mujawar',
        token_type='walk_in',
        status='waiting',
        reason_for_visit='6-Week Immunization (Pentavalent, Rotavirus, PCV) & Weight Check'
    )

    q3 = QueueEntry.objects.create(
        token_number=103,
        patient=pat_aarav,
        clinic_type='pediatric',
        doctor_assigned='Dr. Jalil S. Mujawar',
        token_type='appointment',
        status='waiting',
        reason_for_visit='Seasonal Cough & Fever assessment'
    )

    q4 = QueueEntry.objects.create(
        token_number=104,
        patient=pat_priyanka,
        clinic_type='dental',
        doctor_assigned='Dr. Sabina Firoj Shaikh',
        token_type='walk_in',
        status='completed',
        reason_for_visit='Ultrasonic Teeth Scaling & Polishing',
        completed_time=datetime.datetime.now() - datetime.timedelta(minutes=30)
    )

    # 5. Invoices (Billing Hub)
    Invoice.objects.all().delete()
    inv1 = Invoice.objects.create(
        invoice_no="INV-2026-081",
        patient=pat_rahul,
        family=fam1,
        clinic_type='dental',
        doctor_name='Dr. Sabina Firoj Shaikh',
        items_json=json.dumps([
            {"name": "Root Canal Treatment - Molar (#16)", "qty": 1, "rate": 4500, "total": 4500},
            {"name": "Digital RVG X-Rays (2 Views)", "qty": 2, "rate": 250, "total": 500}
        ]),
        subtotal=Decimal('5000.00'),
        discount=Decimal('500.00'),
        total_amount=Decimal('4500.00'),
        paid_amount=Decimal('2500.00'),
        balance_due=Decimal('2000.00'),
        payment_method='upi',
        payment_status='partial',
        created_by=frontdesk_user,
        notes='Advance paid via GPay. Balance Rs. 2,000 due on crown cementation.'
    )

    inv2 = Invoice.objects.create(
        invoice_no="INV-2026-082",
        patient=pat_kabir,
        family=fam2,
        clinic_type='pediatric',
        doctor_name='Dr. Jalil S. Mujawar',
        items_json=json.dumps([
            {"name": "Pediatric Consultation & Developmental Check", "qty": 1, "rate": 800, "total": 800},
            {"name": "Pentavalent DTP-HepB-Hib + Rotavirus Vaccine", "qty": 1, "rate": 1800, "total": 1800}
        ]),
        subtotal=Decimal('2600.00'),
        discount=Decimal('0.00'),
        total_amount=Decimal('2600.00'),
        paid_amount=Decimal('2600.00'),
        balance_due=Decimal('0.00'),
        payment_method='cash',
        payment_status='paid',
        created_by=frontdesk_user,
        notes='Full payment received in cash.'
    )

    inv3 = Invoice.objects.create(
        invoice_no="INV-2026-083",
        patient=pat_priyanka,
        family=fam1,
        clinic_type='dental',
        doctor_name='Dr. Sabina Firoj Shaikh',
        items_json=json.dumps([
            {"name": "Ultrasonic Scaling & Deep Polishing", "qty": 1, "rate": 1500, "total": 1500}
        ]),
        subtotal=Decimal('1500.00'),
        discount=Decimal('0.00'),
        total_amount=Decimal('1500.00'),
        paid_amount=Decimal('1500.00'),
        balance_due=Decimal('0.00'),
        payment_method='card',
        payment_status='paid',
        created_by=frontdesk_user,
        notes='Paid via POS card machine.'
    )

    # 6. Dental Module Data (Dr. Sabina)
    DentalToothRecord.objects.all().delete()
    # Rahul's odontogram
    DentalToothRecord.objects.create(patient=pat_rahul, tooth_number=16, tooth_type='adult', condition='rct', surface='MOD', notes='Canals obturated with AH Plus & Gutta Percha. Temp Cavit placed.')
    DentalToothRecord.objects.create(patient=pat_rahul, tooth_number=26, tooth_type='adult', condition='caries', surface='Occlusal', notes='Deep dentinal caries. Advised composite restoration.')
    DentalToothRecord.objects.create(patient=pat_rahul, tooth_number=36, tooth_type='adult', condition='crown', surface='All', notes='Zirconia monolithic crown placed 2 years ago, stable.')
    DentalToothRecord.objects.create(patient=pat_rahul, tooth_number=46, tooth_type='adult', condition='implant', surface='Crestal', notes='Nobel Biocare implant with custom abutment.')
    DentalToothRecord.objects.create(patient=pat_rahul, tooth_number=18, tooth_type='adult', condition='missing', surface='', notes='Extracted due to impaction.')
    DentalToothRecord.objects.create(patient=pat_rahul, tooth_number=28, tooth_type='adult', condition='healthy', surface='', notes='Sound enamel.')

    # Treatment Plan
    DentalTreatmentPlan.objects.all().delete()
    DentalTreatmentPlan.objects.create(
        patient=pat_rahul,
        title="Tooth #16 RCT & Zirconia Crown + #26 Restoration",
        total_estimated_cost=Decimal('9500.00'),
        status='active',
        stages_json=json.dumps([
            {"stage": "Visit 1: Diagnostic RVG & Access Opening", "status": "completed", "cost": 1500},
            {"stage": "Visit 2: Biomechanical Prep & Obturation", "status": "completed", "cost": 3000},
            {"stage": "Visit 3: Core Buildup & Crown Digital Scan", "status": "in_progress", "cost": 2000},
            {"stage": "Visit 4: Monolithic Zirconia Crown Cementation", "status": "pending", "cost": 3000}
        ]),
        notes="Patient tolerating treatment well. Mild anesthesia sensitivity noted."
    )

    # Dental Lab Order
    DentalLabOrder.objects.all().delete()
    DentalLabOrder.objects.create(
        patient=pat_rahul,
        lab_name="Apex Dental Craft Wanowrie",
        order_type="zirconia_crown",
        tooth_numbers="16",
        shade="A2 VITA Classic",
        order_date=datetime.date.today() - datetime.timedelta(days=2),
        delivery_due_date=datetime.date.today() + datetime.timedelta(days=2),
        status="in_fabrication",
        cost=Decimal('2200.00'),
        notes="High translucency monolithic zirconia. Strict occlusion clearance 1.5mm."
    )

    # Dental 6-Month Recalls
    DentalRecall.objects.all().delete()
    DentalRecall.objects.create(
        patient=pat_priyanka,
        recall_type="6-Month Routine Hygiene & Checkup",
        due_date=datetime.date.today() + datetime.timedelta(days=7),
        status="pending"
    )
    DentalRecall.objects.create(
        patient=pat_rahul,
        recall_type="Implant Maintenance & Occlusion Review",
        due_date=datetime.date.today() + datetime.timedelta(days=25),
        status="pending"
    )

    # 7. Pediatric Module Data (Dr. Jalil)
    ChildGrowthRecord.objects.all().delete()
    ChildGrowthRecord.objects.create(
        patient=pat_ananya,
        recorded_date=datetime.date.today() - datetime.timedelta(days=30),
        age_months=Decimal('52.0'),
        weight_kg=Decimal('16.4'),
        height_cm=Decimal('103.5'),
        head_circ_cm=Decimal('49.5'),
        bmi=Decimal('15.3'),
        weight_percentile=55,
        height_percentile=60,
        notes="Excellent somatic growth. Active and alert."
    )

    ChildGrowthRecord.objects.create(
        patient=pat_kabir,
        recorded_date=datetime.date.today(),
        age_months=Decimal('2.1'),
        weight_kg=Decimal('5.10'),
        height_cm=Decimal('58.0'),
        head_circ_cm=Decimal('38.2'),
        bmi=Decimal('15.16'),
        weight_percentile=50,
        height_percentile=50,
        notes="Weight gain adequate (approx 30g/day). Clear chest, soft abdomen."
    )

    # Newborn Suite for Baby Kabir
    NewbornRecord.objects.all().delete()
    NewbornRecord.objects.create(
        patient=pat_kabir,
        birth_date=datetime.date(2026, 8, 25),
        birth_time="08:42 AM",
        gestational_age_weeks=Decimal('39.2'),
        birth_weight_kg=Decimal('3.25'),
        birth_length_cm=Decimal('50.5'),
        head_circumference_cm=Decimal('34.8'),
        delivery_type='normal',
        apgar_1min=8,
        apgar_5min=9,
        blood_group='O+',
        maternal_history="Spontaneous conception. Normotensive, GDM negative.",
        phototherapy_required=False,
        phototherapy_hours=0,
        peak_bilirubin_mg_dl=Decimal('7.4'),
        feeding_type='ebf',
        pediatrician_notes="Latching well, vigorous cry, normal primitive reflexes (Moro, Palmar, Sucking)."
    )

    # Vaccination Records
    VaccinationRecord.objects.all().delete()
    # Baby Kabir IAP Schedule
    vax_schedule = [
        {"name": "BCG", "dose": 1, "age": "At Birth", "due": datetime.date(2026, 8, 25), "admin": datetime.date(2026, 8, 26), "status": "administered", "batch": "BCG-9844", "mfg": "Serum Inst of India"},
        {"name": "Oral Polio Vaccine (OPV 0)", "dose": 1, "age": "At Birth", "due": datetime.date(2026, 8, 25), "admin": datetime.date(2026, 8, 26), "status": "administered", "batch": "OPV-2210", "mfg": "Bharat Biotech"},
        {"name": "Hepatitis B (Hep B 1)", "dose": 1, "age": "At Birth", "due": datetime.date(2026, 8, 25), "admin": datetime.date(2026, 8, 26), "status": "administered", "batch": "HB-4091", "mfg": "Serum Inst of India"},
        {"name": "Pentavalent (DTP-HepB-Hib 1)", "dose": 1, "age": "6 Weeks", "due": datetime.date(2026, 10, 6), "admin": None, "status": "due", "batch": "PENTA-7112", "mfg": "Serum Inst of India"},
        {"name": "Rotavirus 1", "dose": 1, "age": "6 Weeks", "due": datetime.date(2026, 10, 6), "admin": None, "status": "due", "batch": "ROTA-3390", "mfg": "Bharat Biotech"},
        {"name": "Pneumococcal (PCV 1)", "dose": 1, "age": "6 Weeks", "due": datetime.date(2026, 10, 6), "admin": None, "status": "due", "batch": "PCV-1082", "mfg": "Pfizer"},
        {"name": "Pentavalent (DTP-HepB-Hib 2)", "dose": 2, "age": "10 Weeks", "due": datetime.date(2026, 11, 3), "admin": None, "status": "due", "batch": "", "mfg": "Serum Inst of India"},
        {"name": "Rotavirus 2", "dose": 2, "age": "10 Weeks", "due": datetime.date(2026, 11, 3), "admin": None, "status": "due", "batch": "", "mfg": "Bharat Biotech"},
        {"name": "Pentavalent (DTP-HepB-Hib 3)", "dose": 3, "age": "14 Weeks", "due": datetime.date(2026, 12, 1), "admin": None, "status": "due", "batch": "", "mfg": "Serum Inst of India"},
        {"name": "Measles-Rubella (MR / MMR 1)", "dose": 1, "age": "9 Months", "due": datetime.date(2027, 5, 25), "admin": None, "status": "due", "batch": "", "mfg": "Serum Inst of India"},
    ]
    for v in vax_schedule:
        VaccinationRecord.objects.create(
            patient=pat_kabir,
            vaccine_name=v['name'],
            dose_number=v['dose'],
            recommended_age_str=v['age'],
            due_date=v['due'],
            administered_date=v['admin'],
            status=v['status'],
            batch_no=v['batch'],
            manufacturer=v['mfg'],
            administered_by='Dr. Jalil S. Mujawar',
            notes="Tolerated well without immediate adverse event." if v['status'] == 'administered' else ""
        )

    # Developmental Milestones for Baby Kabir
    DevelopmentalMilestone.objects.all().delete()
    DevelopmentalMilestone.objects.create(patient=pat_kabir, age_category="2 Months", domain="Gross Motor", milestone_name="Lifts and holds head at 45 degrees in prone position", is_achieved=True, remarks="Good neck muscle tone.")
    DevelopmentalMilestone.objects.create(patient=pat_kabir, age_category="2 Months", domain="Social", milestone_name="Social smile in response to parent face & voice", is_achieved=True, remarks="Smiles responsively to mother.")
    DevelopmentalMilestone.objects.create(patient=pat_kabir, age_category="2 Months", domain="Language", milestone_name="Vocalizes cooing and pleasant gurgling sounds", is_achieved=True, remarks="Cooing actively.")
    DevelopmentalMilestone.objects.create(patient=pat_kabir, age_category="2 Months", domain="Fine Motor", milestone_name="Opens hands and bats at colorful objects", is_achieved=True, remarks="Symmetrical arm movements.")

    # 8. Clinical Prescriptions
    ClinicalPrescription.objects.all().delete()
    ClinicalPrescription.objects.create(
        patient=pat_rahul,
        clinic_type='dental',
        doctor_name='Dr. Sabina Firoj Shaikh',
        diagnosis='Acute Irreversible Pulpitis #16, Symptomatic Apical Periodontitis',
        chief_complaints='Severe throbbing pain in upper right back tooth, radiating to temple.',
        vitals_json=json.dumps({"bp": "124/82 mmHg", "pulse": "76 bpm", "temp": "98.4 F"}),
        medicines_json=json.dumps([
            {"drug": "Augmentin 625 Duo (Amoxicillin + Clav)", "dosage": "1 tablet twice daily", "duration": "5 days", "notes": "After food with full glass of water"},
            {"drug": "Ketorol DT 10mg", "dosage": "1 tablet as needed (SOS max 3/day)", "duration": "3 days", "notes": "Disperse in half glass water after meals for acute pain"},
            {"drug": "Hexidine 0.2% Mouthwash", "dosage": "10 ml rinse for 60 seconds", "duration": "7 days", "notes": "Morning and night, do not eat for 30 mins after"}
        ]),
        diet_instructions="Chew on the left side. Avoid hard, crunchy, or very hot beverages.",
        investigations_advised="Digital RVG Radiograph of #16 post obturation.",
        follow_up_date="Tuesday, 11:30 AM for core buildup and crown scan."
    )

    ClinicalPrescription.objects.create(
        patient=pat_aarav,
        clinic_type='pediatric',
        doctor_name='Dr. Jalil S. Mujawar',
        diagnosis='Acute Viral Upper Respiratory Infection (URTI) with Low Grade Fever',
        chief_complaints='Runny nose, nighttime dry cough, mild fever 99.8 F for 2 days.',
        vitals_json=json.dumps({"weight": "16.2 kg", "temp": "99.4 F", "spo2": "99%", "resp_rate": "24/min"}),
        medicines_json=json.dumps([
            {"drug": "Syrup Crocin 240mg / 5ml", "dosage": "5 ml every 6 hours SOS", "duration": "3 days", "notes": "Only if temperature exceeds 100 F. Never exceed 4 doses/day."},
            {"drug": "Syrup Levolin (Levosalbutamol)", "dosage": "2.5 ml twice daily", "duration": "4 days", "notes": "Helps relieve nighttime bronchial coughing."},
            {"drug": "Nasoclear Saline Nasal Drops", "dosage": "2 drops each nostril TID", "duration": "5 days", "notes": "Before feeds and before bedtime to clear nasal congestion."}
        ]),
        diet_instructions="Offer warm soups, fresh fluids, steam inhalation twice daily.",
        investigations_advised="None needed currently. Review if fever persists beyond 72 hours.",
        follow_up_date="After 3 days or SOS if breathing fast or poor oral intake."
    )

    # 9. Audit Logs
    AuditLog.objects.all().delete()
    AuditLog.objects.create(
        user=admin_user,
        user_email=admin_user.email,
        action_type='CREATE',
        target_model='StaffProfile',
        target_id='1',
        summary='System initialized with 4 RBAC role profiles (Admin, Front Desk, Dental, Pediatric).',
        ip_address='127.0.0.1'
    )
    AuditLog.objects.create(
        user=frontdesk_user,
        user_email=frontdesk_user.email,
        action_type='BILLING',
        target_model='Invoice',
        target_id=inv1.invoice_no,
        summary='Created Invoice INV-2026-081 (Rs. 4,500) for Rahul Kulkarni. Recorded advance payment Rs. 2,500 via UPI.',
        ip_address='127.0.0.1'
    )

    # 10. Today's Appointments & Incoming Booking Requests
    AppointmentRequest.objects.all().delete()
    # Today's Upcoming
    apt1 = AppointmentRequest.objects.create(
        clinic_type='dental',
        patient_name='Rahul Kulkarni',
        parent_name='',
        phone_number='9822012345',
        service_needed='Root Canal Molar Obturation (#16)',
        preferred_date='Today',
        preferred_time='11:30 AM',
        notes='Patient arrived on time. Follow-up for canal obturation.',
        status='accepted'
    )
    apt2 = AppointmentRequest.objects.create(
        clinic_type='pediatric',
        patient_name='Aarav Mehta (4 yrs)',
        parent_name='Sneha Mehta',
        phone_number='9890123456',
        service_needed='Pediatric Cough & Growth Checkup',
        preferred_date='Today',
        preferred_time='05:30 PM',
        notes='Mild viral cough, requested Dr. Jalil evening slot.',
        status='accepted'
    )
    # Today's Completed
    apt3 = AppointmentRequest.objects.create(
        clinic_type='dental',
        patient_name='Priyanka Kulkarni',
        parent_name='',
        phone_number='9822012345',
        service_needed='Ultrasonic Teeth Scaling & Polishing',
        preferred_date='Today',
        preferred_time='10:00 AM',
        notes='Session completed smoothly. Advised soft brushing.',
        status='completed'
    )
    # New Incoming Requests (Inbox)
    apt4 = AppointmentRequest.objects.create(
        clinic_type='dental',
        patient_name='Dr. Nilesh Matkari',
        parent_name='',
        phone_number='9922114455',
        service_needed='Zirconia Crown Consultation',
        preferred_date='Tomorrow',
        preferred_time='12:00 PM',
        notes='Referred by Dr. Sabina. Needs crown assessment for upper premolar.',
        status='pending'
    )
    apt5 = AppointmentRequest.objects.create(
        clinic_type='pediatric',
        patient_name='Baby Anvi Sharma (6 mos)',
        parent_name='Vikram Sharma',
        phone_number='9823456780',
        service_needed='Weaning Diet & 6-Month Flu Vaccine',
        preferred_date='Tomorrow',
        preferred_time='06:15 PM',
        notes='First time consultation with Dr. Jalil.',
        status='pending'
    )

    # 11. Scheduled Reminders
    from clinic.models import ScheduledReminder, WhatsAppThread, WhatsAppChatMessage
    ScheduledReminder.objects.all().delete()
    ScheduledReminder.objects.create(
        patient=pat_rahul,
        preset_type='Crown / Cap Fitting',
        custom_reason='Monolithic Zirconia Crown Fitting (#16)',
        target_date=datetime.date.today() + datetime.timedelta(days=3),
        target_time='11:30 AM',
        status='queued'
    )
    ScheduledReminder.objects.create(
        patient=pat_kabir,
        preset_type='Vaccine Booster',
        custom_reason='10-Week Pentavalent & Rotavirus Booster',
        target_date=datetime.date.today() + datetime.timedelta(days=12),
        target_time='05:30 PM',
        status='queued'
    )
    ScheduledReminder.objects.create(
        patient=pat_priyanka,
        preset_type='6-Month Dental Cleaning',
        custom_reason='6-Month Routine Hygiene Checkup & Scaling',
        target_date=datetime.date.today() + datetime.timedelta(days=180),
        target_time='10:30 AM',
        status='queued'
    )

    # 12. WhatsApp Interactive Threads & History
    WhatsAppThread.objects.all().delete()
    th1 = WhatsAppThread.objects.create(
        patient=pat_rahul,
        last_message='Thank you Dr. Sabina, pain is much better. See you at 11:30 AM.',
        unread_count=0
    )
    WhatsAppChatMessage.objects.create(
        thread=th1,
        sender='clinic',
        text='Hello Rahul, your dental appointment with Dr. Sabina is confirmed for Today at 11:30 AM. Wanowrie Clinic.'
    )
    WhatsAppChatMessage.objects.create(
        thread=th1,
        sender='patient',
        text='Thank you Dr. Sabina, pain is much better. See you at 11:30 AM.'
    )

    th2 = WhatsAppThread.objects.create(
        patient=pat_aarav,
        last_message='Understood, bringing Aarav around 5:30 PM.',
        unread_count=1
    )
    WhatsAppChatMessage.objects.create(
        thread=th2,
        sender='clinic',
        text='Hello Sneha, Dr. Jalil is available at 5:30 PM today for Aarav\'s checkup. Please bring his vaccination card.'
    )
    WhatsAppChatMessage.objects.create(
        thread=th2,
        sender='patient',
        text='Understood, bringing Aarav around 5:30 PM.'
    )

    th3 = WhatsAppThread.objects.create(
        patient=pat_kabir,
        last_message='Receipt INV-2026-082 for Rs. 2,600 sent via WhatsApp.',
        unread_count=0
    )
    WhatsAppChatMessage.objects.create(
        thread=th3,
        sender='clinic',
        text='Dear Amit Deshmukh, thank you for visiting Buds Child Clinic. Payment Receipt INV-2026-082 for Rs. 2,600 has been verified.'
    )

    print("✅ Seed script finished successfully with all test accounts, today desk, patients, invoices, reminders and WhatsApp threads!")

if __name__ == '__main__':
    seed()
