# dental

**Roots Dental Clinic & Buds Child Clinic — Wanowrie, Pune**
> Dual-specialty premium medical website & front-desk CRM engine.

## 🌟 Clinic Highlights
- **Roots Dental Clinic**: Led by **Dr. Sabina Firoj Shaikh** (MDS Gold Medalist, Prosthodontist & Oral Implantologist). Advanced, painless single-visit root canals, clear aligners, and precision smile makeovers.
- **Buds Child Clinic**: Led by **Dr. Jalil S. Mujawar** (Senior Consultant Pediatrician & Neonatologist, MBBS DCH, 15+ years experience). Trusted by 75,000+ parents in Wanowrie.

## 🚀 Key Features
- **Apple iOS Liquid Glass UI**: Frosted glassmorphism, responsive navigation, and fluid interaction design.
- **Zero-Scroll Mobile Booking Sheet**: Native iOS 17/18-style bottom modal sheet with direct slot reservation.
- **WhatsApp Confirmation Flow**: Real-time slot requests routed to front desk via automated WhatsApp pre-filled messages.
- **Dual Practice Switcher**: Instant crossfading between Dental and Pediatric clinic services.
- **Lightweight Front-Desk CRM**: In-browser appointment triage, search, and status tracking.

## 🛠️ Tech Stack
- **Backend**: Django 5.1 (Python 3.12+)
- **Frontend**: Tailwind CSS CDN, Lucide Icons, Vanilla JavaScript / Framer Motion
- **Database**: SQLite3 (pre-configured)

## 🏃 Local Setup & Run
```bash
# Clone the repository
git clone https://github.com/Irfanshkhdev/dental.git
cd dental

# Create & activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run migrations & launch local server
cd dental_clinic_django
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
