/**
 * Roots Dental & Buds Child Clinic — Interactive Liquid Glass Engine
 * Features:
 *  1. Native iOS 17/18-style Zero-Scroll Booking Modal Sheet (openBookingModal / closeBookingModal)
 *  2. Morphing Booking Split-Panel state machine with guaranteed image visibility
 *  3. Contextual routing: Mobile 1-tap sheet vs Desktop header-offset smooth scrolling
 *  4. Request-based booking submission to Django AJAX API (/api/book/) with WhatsApp confirmation
 *  5. Mobile drawer navigation and scroll-aware glass header blur
 */

(function () {
  'use strict';

  // Service datasets for dynamic dropdowns
  const DENTAL_SERVICES = [
    'General Dentistry & Routine Checkup',
    'Root Canal Treatment (Single-Sitting)',
    'Braces & Clear Invisible Aligners',
    'Pediatric Dentistry (Kids Care)',
    'Cosmetic Smile Makeover & Veneers',
    'Dental Implants & Replacement',
    'Gum Care & Laser Therapy',
    'Emergency Toothache Relief'
  ];

  const PEDIATRIC_SERVICES = [
    'Newborn Intensive Care & Jaundice',
    'Vaccination & Immunization (IAP)',
    'Growth & Developmental Milestone Check',
    'Childhood Fever & Illness Assessment',
    'Infant Feeding & Lactation Guidance',
    'Pediatric Allergy & Asthma Care',
    'Behavioral & Learning Milestones',
    'Adolescent Health Consultation'
  ];

  // Current active clinic state
  let currentClinic = 'dental';

  // -------------------------------------------------------------
  // 1. IN-PAGE MORPHING BOOKING STATE MACHINE (#booking-wrapper)
  // -------------------------------------------------------------
  window.switchClinicBooking = function (type, preselectedService) {
    currentClinic = type;

    const formClinicInput = document.getElementById('form-clinic-type');
    const doctorPanel = document.getElementById('dynamic-doctor-panel');
    const clinicTag = document.getElementById('panel-clinic-tag');
    const doctorName = document.getElementById('panel-doctor-name');
    const doctorTitle = document.getElementById('panel-doctor-title');
    const doctorImg = document.getElementById('panel-doctor-img');
    const badgeTopIcon = document.getElementById('badge-top-icon');
    const badgeTopText = document.getElementById('badge-top-text');
    const badgeBottomIcon = document.getElementById('badge-bottom-icon');
    const badgeBottomText = document.getElementById('badge-bottom-text');
    const guaranteeText = document.getElementById('panel-guarantee-text');

    const btnDental = document.getElementById('btn-toggle-dental');
    const btnPediatric = document.getElementById('btn-toggle-pediatric');

    const mobilePill = document.getElementById('mobile-doctor-pill');
    const mobileAvatar = document.getElementById('mobile-pill-avatar');
    const mobilePillName = document.getElementById('mobile-pill-name');
    const mobilePillDesc = document.getElementById('mobile-pill-desc');
    const mobilePillBadge = document.getElementById('mobile-pill-badge');

    const labelPatient = document.getElementById('label-patient-name');
    const inputPatient = document.getElementById('patient-name');
    const parentNameGroup = document.getElementById('parent-name-group');
    const inputParent = document.getElementById('parent-name');
    const serviceSelect = document.getElementById('service-needed');
    const submitBtn = document.getElementById('btn-submit-booking');
    const submitBtnText = document.getElementById('submit-btn-text');
    const bookingPill = document.getElementById('booking-pill');

    if (formClinicInput) formClinicInput.value = type;

    if (type === 'dental') {
      // 1. Left Panel (Desktop): Slate Blue
      if (doctorPanel) {
        doctorPanel.className = 'hidden lg:flex lg:col-span-5 relative p-8 sm:p-10 flex-col justify-between overflow-hidden bg-gradient-to-br from-dental-600 to-dental-800 text-white transition-all duration-700 ease-in-out';
      }
      if (clinicTag) clinicTag.textContent = 'Roots Dental Clinic';
      if (doctorName) doctorName.textContent = 'Dr. Sabina Firoj Shaikh';
      if (doctorTitle) doctorTitle.textContent = 'MDS Gold Medalist • Prosthodontics • 10+ Yrs Clinical Mastery';
      if (guaranteeText) guaranteeText.textContent = 'Painless Protocol • Guaranteed No Double-Booking';

      // Desktop Doctor Image: Smooth crossfade & scale
      if (doctorImg) {
        doctorImg.style.transition = 'opacity 0.25s ease-out, transform 0.25s ease-out';
        doctorImg.style.opacity = '0';
        doctorImg.style.transform = 'scale(0.97)';
        setTimeout(() => {
          doctorImg.src = '/static/images/dentist_sabina.png';
          doctorImg.alt = 'Dr. Sabina Firoj Shaikh';
          doctorImg.style.opacity = '1';
          doctorImg.style.transform = 'scale(1)';
        }, 120);
      }

      // Badges
      if (badgeTopIcon) badgeTopIcon.textContent = '🦷';
      if (badgeTopText) badgeTopText.textContent = 'Painless Care';
      if (badgeBottomIcon) badgeBottomIcon.textContent = '🏅';
      if (badgeBottomText) badgeBottomText.textContent = 'MDS Gold Medalist';

      // Mobile Compact Doctor Pill (Above toggle)
      if (mobilePill) {
        mobilePill.className = 'lg:hidden flex items-center gap-3 p-3 rounded-2xl bg-dental-50 border border-dental-200/80 mb-4 transition-all';
      }
      if (mobileAvatar) mobileAvatar.src = '/static/images/dentist_sabina.png';
      if (mobilePillName) mobilePillName.textContent = 'Dr. Sabina Firoj Shaikh';
      if (mobilePillDesc) mobilePillDesc.textContent = 'MDS Gold Medalist • Prosthodontist';
      if (mobilePillBadge) {
        mobilePillBadge.className = 'px-2.5 py-1 rounded-full bg-white text-dental-700 text-[10px] font-heading font-bold shadow-xs border border-dental-200 flex-shrink-0';
        mobilePillBadge.textContent = '5.0 ⭐';
      }

      // Toggle Buttons Active State
      if (btnDental) {
        btnDental.className = 'flex-1 py-3 px-4 rounded-xl font-heading font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all duration-300 bg-white text-dental-700 shadow-md';
      }
      if (btnPediatric) {
        btnPediatric.className = 'flex-1 py-3 px-4 rounded-xl font-heading font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all duration-300 text-slate-500 hover:text-slate-800';
      }

      // Form Adjustments
      if (labelPatient) labelPatient.innerHTML = 'Patient Full Name <span class="text-rose-500">*</span>';
      if (inputPatient) inputPatient.placeholder = 'e.g. Rahul Kulkarni';
      if (parentNameGroup) {
        parentNameGroup.classList.add('hidden');
        if (inputParent) inputParent.removeAttribute('required');
      }

      // Populate Dental Services
      if (serviceSelect) {
        serviceSelect.innerHTML = '';
        DENTAL_SERVICES.forEach(s => {
          const opt = document.createElement('option');
          opt.value = s;
          opt.textContent = s;
          if (preselectedService && s.toLowerCase().includes(preselectedService.toLowerCase())) {
            opt.selected = true;
          }
          serviceSelect.appendChild(opt);
        });
      }

      // Submit Button Style
      if (submitBtn) {
        submitBtn.className = 'w-full py-4 px-6 rounded-2xl font-heading font-bold text-sm text-white bg-dental-600 hover:bg-dental-700 shadow-xl shadow-dental-700/25 active:scale-98 transition-all duration-300 flex items-center justify-center gap-2';
      }
      if (submitBtnText) submitBtnText.textContent = 'Request Dental Appointment';

      if (bookingPill) {
        bookingPill.className = 'px-4 py-1.5 rounded-full bg-dental-100 text-dental-700 text-xs font-heading font-bold uppercase tracking-wider transition-colors duration-500';
        bookingPill.textContent = '🦷 Roots Dental Request Engine';
      }

    } else {
      // 2. Left Panel (Desktop): Sage Green
      if (doctorPanel) {
        doctorPanel.className = 'hidden lg:flex lg:col-span-5 relative p-8 sm:p-10 flex-col justify-between overflow-hidden bg-gradient-to-br from-pediatric-600 to-pediatric-800 text-white transition-all duration-700 ease-in-out';
      }
      if (clinicTag) clinicTag.textContent = 'Buds Child Clinic';
      if (doctorName) doctorName.textContent = 'Dr. Jalil S. Mujawar';
      if (doctorTitle) doctorTitle.textContent = 'Senior Consultant Pediatrician • MBBS, DCH • 15+ Yrs Clinical Mastery';
      if (guaranteeText) guaranteeText.textContent = 'Trusted by 75,400+ Mothers in Wanowrie';

      // Desktop Doctor Image: Smooth crossfade & scale
      if (doctorImg) {
        doctorImg.style.transition = 'opacity 0.25s ease-out, transform 0.25s ease-out';
        doctorImg.style.opacity = '0';
        doctorImg.style.transform = 'scale(0.97)';
        setTimeout(() => {
          doctorImg.src = '/static/images/pediatrician_jalil.png';
          doctorImg.alt = 'Dr. Jalil S. Mujawar';
          doctorImg.style.opacity = '1';
          doctorImg.style.transform = 'scale(1)';
        }, 120);
      }

      // Badges
      if (badgeTopIcon) badgeTopIcon.textContent = '🍼';
      if (badgeTopText) badgeTopText.textContent = 'Newborn Specialist';
      if (badgeBottomIcon) badgeBottomIcon.textContent = '🛡️';
      if (badgeBottomText) badgeBottomText.textContent = '75k+ Parents Trust';

      // Mobile Compact Doctor Pill (Above toggle)
      if (mobilePill) {
        mobilePill.className = 'lg:hidden flex items-center gap-3 p-3 rounded-2xl bg-pediatric-50 border border-pediatric-200/80 mb-4 transition-all';
      }
      if (mobileAvatar) mobileAvatar.src = '/static/images/pediatrician_jalil.png';
      if (mobilePillName) mobilePillName.textContent = 'Dr. Jalil S. Mujawar';
      if (mobilePillDesc) mobilePillDesc.textContent = 'Senior Consultant Pediatrician • MBBS, DCH';
      if (mobilePillBadge) {
        mobilePillBadge.className = 'px-2.5 py-1 rounded-full bg-white text-pediatric-700 text-[10px] font-heading font-bold shadow-xs border border-pediatric-200 flex-shrink-0';
        mobilePillBadge.textContent = '75k+ 🛡️';
      }

      // Toggle Buttons Active State
      if (btnDental) {
        btnDental.className = 'flex-1 py-3 px-4 rounded-xl font-heading font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all duration-300 text-slate-500 hover:text-slate-800';
      }
      if (btnPediatric) {
        btnPediatric.className = 'flex-1 py-3 px-4 rounded-xl font-heading font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all duration-300 bg-white text-pediatric-700 shadow-md';
      }

      // Form Adjustments
      if (labelPatient) labelPatient.innerHTML = "Child's Full Name <span class=\"text-rose-500\">*</span>";
      if (inputPatient) inputPatient.placeholder = 'e.g. Aarav Mehta (4 yrs)';
      if (parentNameGroup) {
        parentNameGroup.classList.remove('hidden');
        if (inputParent) inputParent.setAttribute('required', 'required');
      }

      // Populate Pediatric Services
      if (serviceSelect) {
        serviceSelect.innerHTML = '';
        PEDIATRIC_SERVICES.forEach(s => {
          const opt = document.createElement('option');
          opt.value = s;
          opt.textContent = s;
          if (preselectedService && s.toLowerCase().includes(preselectedService.toLowerCase())) {
            opt.selected = true;
          }
          serviceSelect.appendChild(opt);
        });
      }

      // Submit Button Style
      if (submitBtn) {
        submitBtn.className = 'w-full py-4 px-6 rounded-2xl font-heading font-bold text-sm text-white bg-pediatric-600 hover:bg-pediatric-700 shadow-xl shadow-pediatric-700/25 active:scale-98 transition-all duration-300 flex items-center justify-center gap-2';
      }
      if (submitBtnText) submitBtnText.textContent = 'Request Child Care Appointment';

      if (bookingPill) {
        bookingPill.className = 'px-4 py-1.5 rounded-full bg-pediatric-100 text-pediatric-800 text-xs font-heading font-bold uppercase tracking-wider transition-colors duration-500';
        bookingPill.textContent = '👶 Buds Pediatric Request Engine';
      }
    }
  };


  // -------------------------------------------------------------
  // 2. APPLE iOS 17/18 ZERO-SCROLL BOOKING MODAL SHEET
  // -------------------------------------------------------------
  window.openBookingModal = function (targetClinic) {
    try {
      const modal = document.getElementById('mobile-booking-modal');
      const sheet = document.getElementById('modal-sheet');
      if (!modal || !sheet) {
        console.warn('Booking modal elements not found, scrolling to booking wrapper instead.');
        window.scrollToBooking(targetClinic);
        return;
      }

      // Detect clinic if not passed
      let clinicToSet = targetClinic;
      if (!clinicToSet || (clinicToSet !== 'dental' && clinicToSet !== 'pediatric')) {
        clinicToSet = window.location.pathname.includes('pediatric') ? 'pediatric' : 'dental';
      }

      if (typeof window.setModalClinic === 'function') {
        window.setModalClinic(clinicToSet);
      }

      // Set default tomorrow date if empty
      const modalDate = document.getElementById('modal-preferred-date');
      if (modalDate && !modalDate.value) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        modalDate.value = tomorrow.toISOString().split('T')[0];
        modalDate.min = new Date().toISOString().split('T')[0];
      }

      // Force display flex before animation
      modal.style.display = 'flex';
      modal.style.pointerEvents = 'auto';

      requestAnimationFrame(function () {
        modal.classList.remove('pointer-events-none', 'opacity-0');
        modal.classList.add('opacity-100');

        sheet.style.transform = 'translateY(0)';
        sheet.classList.remove('translate-y-full');
        sheet.classList.add('translate-y-0');
      });

      // Prevent body bounce behind modal on mobile
      if (window.innerWidth < 768) {
        document.body.style.overflow = 'hidden';
      }

      if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
      }
    } catch (err) {
      console.error('Error in openBookingModal:', err);
    }
  };

  window.closeBookingModal = function () {
    try {
      const modal = document.getElementById('mobile-booking-modal');
      const sheet = document.getElementById('modal-sheet');
      if (!modal || !sheet) return;

      sheet.style.transform = '';
      sheet.classList.remove('translate-y-0');
      sheet.classList.add('translate-y-full');

      modal.classList.remove('opacity-100');
      modal.classList.add('opacity-0', 'pointer-events-none');

      setTimeout(() => {
        modal.style.display = 'none';
        modal.style.pointerEvents = 'none';
        document.body.style.overflow = '';
      }, 220);
    } catch (err) {
      console.error('Error in closeBookingModal:', err);
    }
  };

  window.setModalClinic = function (type) {
    const modalClinicInput = document.getElementById('modal-clinic-type');
    const btnDental = document.getElementById('modal-toggle-dental');
    const btnPediatric = document.getElementById('modal-toggle-pediatric');
    const banner = document.getElementById('modal-doctor-banner');
    const avatar = document.getElementById('modal-doctor-avatar');
    const name = document.getElementById('modal-doctor-name');
    const desc = document.getElementById('modal-doctor-desc');
    const badge = document.getElementById('modal-doctor-badge');
    const labelPatient = document.getElementById('modal-label-patient');
    const inputPatient = document.getElementById('modal-patient-name');
    const parentGroup = document.getElementById('modal-parent-group');
    const inputParent = document.getElementById('modal-parent-name');
    const selectService = document.getElementById('modal-service-needed');
    const submitBtn = document.getElementById('modal-submit-btn');
    const submitText = document.getElementById('modal-submit-text');

    if (modalClinicInput) modalClinicInput.value = type;

    if (type === 'dental') {
      if (btnDental) {
        btnDental.className = 'flex-1 py-2 px-3 rounded-xl font-heading font-bold text-xs flex items-center justify-center gap-1.5 transition-all bg-white text-dental-700 shadow-sm';
      }
      if (btnPediatric) {
        btnPediatric.className = 'flex-1 py-2 px-3 rounded-xl font-heading font-semibold text-xs flex items-center justify-center gap-1.5 transition-all text-slate-500 hover:text-slate-800';
      }

      if (banner) {
        banner.className = 'flex items-center gap-3 p-3 rounded-2xl bg-dental-50/90 border border-dental-200/80 mb-3.5 transition-all';
      }
      if (avatar) avatar.src = '/static/images/dentist_sabina.png';
      if (name) name.textContent = 'Dr. Sabina Firoj Shaikh';
      if (desc) desc.textContent = 'MDS Gold Medalist • Prosthodontist';
      if (badge) {
        badge.className = 'px-2.5 py-1 rounded-full bg-white text-dental-700 text-[10px] font-heading font-bold shadow-xs border border-dental-200';
        badge.textContent = '5.0 ⭐';
      }

      if (labelPatient) labelPatient.innerHTML = 'Patient Full Name <span class="text-rose-500">*</span>';
      if (inputPatient) inputPatient.placeholder = 'e.g. Rahul Kulkarni';

      if (parentGroup) {
        parentGroup.classList.add('hidden');
        if (inputParent) inputParent.removeAttribute('required');
      }

      if (selectService) {
        selectService.innerHTML = '';
        DENTAL_SERVICES.forEach(s => {
          const opt = document.createElement('option');
          opt.value = s;
          opt.textContent = s;
          selectService.appendChild(opt);
        });
      }

      if (submitBtn) {
        submitBtn.className = 'w-full mt-2 py-3.5 px-5 rounded-2xl font-heading font-bold text-xs sm:text-sm text-white bg-dental-600 hover:bg-dental-700 shadow-lg shadow-dental-700/25 active:scale-98 transition flex items-center justify-center gap-2';
      }
      if (submitText) submitText.textContent = 'Request Dental Appointment';

    } else {
      if (btnDental) {
        btnDental.className = 'flex-1 py-2 px-3 rounded-xl font-heading font-semibold text-xs flex items-center justify-center gap-1.5 transition-all text-slate-500 hover:text-slate-800';
      }
      if (btnPediatric) {
        btnPediatric.className = 'flex-1 py-2 px-3 rounded-xl font-heading font-bold text-xs flex items-center justify-center gap-1.5 transition-all bg-white text-pediatric-700 shadow-sm';
      }

      if (banner) {
        banner.className = 'flex items-center gap-3 p-3 rounded-2xl bg-pediatric-50/90 border border-pediatric-200/80 mb-3.5 transition-all';
      }
      if (avatar) avatar.src = '/static/images/pediatrician_jalil.png';
      if (name) name.textContent = 'Dr. Jalil S. Mujawar';
      if (desc) desc.textContent = 'Senior Consultant Pediatrician • MBBS, DCH';
      if (badge) {
        badge.className = 'px-2.5 py-1 rounded-full bg-white text-pediatric-700 text-[10px] font-heading font-bold shadow-xs border border-pediatric-200';
        badge.textContent = '75k+ 🛡️';
      }

      if (labelPatient) labelPatient.innerHTML = "Child's Full Name <span class=\"text-rose-500\">*</span>";
      if (inputPatient) inputPatient.placeholder = 'e.g. Aarav Mehta (4 yrs)';

      if (parentGroup) {
        parentGroup.classList.remove('hidden');
        if (inputParent) inputParent.setAttribute('required', 'required');
      }

      if (selectService) {
        selectService.innerHTML = '';
        PEDIATRIC_SERVICES.forEach(s => {
          const opt = document.createElement('option');
          opt.value = s;
          opt.textContent = s;
          selectService.appendChild(opt);
        });
      }

      if (submitBtn) {
        submitBtn.className = 'w-full mt-2 py-3.5 px-5 rounded-2xl font-heading font-bold text-xs sm:text-sm text-white bg-pediatric-600 hover:bg-pediatric-700 shadow-lg shadow-pediatric-700/25 active:scale-98 transition flex items-center justify-center gap-2';
      }
      if (submitText) submitText.textContent = 'Request Child Care Appointment';
    }
  };

  // Submission handler for Modal Form
  window.handleModalBookingSubmit = function (e) {
    e.preventDefault();

    const submitBtn = document.getElementById('modal-submit-btn');
    const submitText = document.getElementById('modal-submit-text');
    const toast = document.getElementById('modal-toast');
    const toastMsg = document.getElementById('modal-toast-msg');
    const toastWa = document.getElementById('modal-toast-wa');
    const toastWaLink = document.getElementById('modal-toast-wa-link');

    const payload = {
      clinic_type: document.getElementById('modal-clinic-type').value,
      patient_name: document.getElementById('modal-patient-name').value.trim(),
      parent_name: (document.getElementById('modal-parent-name') ? document.getElementById('modal-parent-name').value.trim() : ''),
      phone_number: document.getElementById('modal-phone-number').value.trim(),
      service_needed: document.getElementById('modal-service-needed').value,
      preferred_date: document.getElementById('modal-preferred-date').value,
      preferred_time: document.getElementById('modal-preferred-time').value,
      notes: ''
    };

    if (!payload.patient_name || !payload.phone_number || !payload.preferred_date) {
      alert('Please fill out all required fields.');
      return;
    }

    const originalText = submitText ? submitText.textContent : 'Request Appointment';
    if (submitBtn) submitBtn.disabled = true;
    if (submitText) submitText.textContent = 'Reserving Slot...';

    fetch('/api/book/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      if (submitBtn) submitBtn.disabled = false;
      if (submitText) submitText.textContent = originalText;

      if (data.status === 'success') {
        if (toast) {
          toast.classList.remove('hidden');
          if (toastMsg) {
            toastMsg.textContent = `Hello ${data.patient_name}, your request is locked in! Our front desk is confirming your exact slot on WhatsApp.`;
          }
          if (toastWa && data.whatsapp_url) {
            toastWa.classList.remove('hidden');
            if (toastWaLink) toastWaLink.href = data.whatsapp_url;
          }
        }

        // Reset inputs
        const form = document.getElementById('modal-appointment-form');
        if (form) form.reset();
        document.getElementById('modal-clinic-type').value = payload.clinic_type;
        window.setModalClinic(payload.clinic_type);
      } else {
        alert(data.message || 'Error saving request. Please call our clinic.');
      }
    })
    .catch(err => {
      if (submitBtn) submitBtn.disabled = false;
      if (submitText) submitText.textContent = originalText;
      console.error('Modal Booking API error:', err);
      alert('Network issue. Reach us directly on WhatsApp at +91 98765 43210.');
    });
  };


  // -------------------------------------------------------------
  // 3. CONTEXTUAL ROUTING (Mobile: Modal Sheet | Desktop: Smooth Scroll)
  // -------------------------------------------------------------
  window.scrollToBooking = function (targetClinic, serviceName) {
    // If user is on a mobile device, open the zero-scroll iOS sheet directly!
    if (window.innerWidth < 768) {
      window.openBookingModal(targetClinic);
      return;
    }

    const bookingWrapper = document.getElementById('booking-wrapper');

    if (bookingWrapper) {
      if (targetClinic) {
        window.switchClinicBooking(targetClinic, serviceName);
      }

      const siteHeader = document.getElementById('site-header');
      const headerHeight = siteHeader ? siteHeader.offsetHeight : 80;
      const rect = bookingWrapper.getBoundingClientRect();
      const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;
      const destinationY = rect.top + currentScrollY - headerHeight - 16;

      window.scrollTo({
        top: Math.max(0, destinationY),
        behavior: 'smooth'
      });
    } else {
      // User is on /about, /gallery, or /contact: redirect to home or pediatric page with hash
      const destUrl = (targetClinic === 'pediatric') ? '/pediatric/#booking-wrapper' : '/dental/#booking-wrapper';
      window.location.href = destUrl;
    }
  };


  // -------------------------------------------------------------
  // 4. HEADER & NAVIGATION BUTTON INTERCEPTORS
  // -------------------------------------------------------------
  function setupBookingButtonInterceptors() {
    const headerBtn = document.getElementById('header-book-btn');
    const mobileBottomBtn = document.getElementById('mobile-bottom-book-btn');
    const mobileDrawerBtn = document.getElementById('mobile-drawer-book-btn');

    // Header Book Appointment Click
    if (headerBtn) {
      headerBtn.addEventListener('click', function (e) {
        e.preventDefault();
        const path = window.location.pathname;
        const clinic = path.includes('pediatric') ? 'pediatric' : 'dental';

        if (window.innerWidth < 768) {
          window.openBookingModal(clinic);
        } else {
          window.scrollToBooking(clinic);
        }
      });
    }

    // Mobile Fixed Bottom Bar "Book Now" Click
    if (mobileBottomBtn) {
      mobileBottomBtn.addEventListener('click', function (e) {
        e.preventDefault();
        const path = window.location.pathname;
        const clinic = path.includes('pediatric') ? 'pediatric' : 'dental';
        window.openBookingModal(clinic);
      });
    }

    // Mobile Drawer "Book Appointment" Click
    if (mobileDrawerBtn) {
      mobileDrawerBtn.addEventListener('click', function (e) {
        e.preventDefault();
        closeMobileDrawer();
        const path = window.location.pathname;
        const clinic = path.includes('pediatric') ? 'pediatric' : 'dental';
        setTimeout(() => {
          window.openBookingModal(clinic);
        }, 150);
      });
    }
  }


  // -------------------------------------------------------------
  // 5. IN-PAGE FORM SUBMISSION (/api/book/)
  // -------------------------------------------------------------
  window.handleBookingSubmit = function (e) {
    e.preventDefault();

    const form = document.getElementById('appointment-form');
    const submitBtn = document.getElementById('btn-submit-booking');
    const submitBtnText = document.getElementById('submit-btn-text');
    const toast = document.getElementById('booking-toast');
    const toastMsg = document.getElementById('toast-message');
    const toastWaAction = document.getElementById('toast-whatsapp-action');
    const toastWaLink = document.getElementById('toast-whatsapp-link');

    const payload = {
      clinic_type: document.getElementById('form-clinic-type').value,
      patient_name: document.getElementById('patient-name').value.trim(),
      parent_name: (document.getElementById('parent-name') ? document.getElementById('parent-name').value.trim() : ''),
      phone_number: document.getElementById('phone-number').value.trim(),
      service_needed: document.getElementById('service-needed').value,
      preferred_date: document.getElementById('preferred-date').value,
      preferred_time: document.getElementById('preferred-time').value,
      notes: document.getElementById('notes').value.trim()
    };

    if (!payload.patient_name || !payload.phone_number || !payload.preferred_date) {
      alert('Please fill out all required fields marked with *');
      return;
    }

    const originalText = submitBtnText.textContent;
    submitBtn.disabled = true;
    submitBtnText.textContent = 'Reserving Your Slot...';

    fetch('/api/book/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      submitBtn.disabled = false;
      submitBtnText.textContent = originalText;

      if (data.status === 'success') {
        if (toast) {
          toast.classList.remove('hidden');
          if (toastMsg) {
            toastMsg.textContent = `Hello ${data.patient_name}, your request for ${payload.clinic_type === 'dental' ? 'Roots Dental Clinic' : 'Buds Child Clinic'} has been submitted! Our front desk will confirm your exact time on WhatsApp.`;
          }
          if (toastWaAction && data.whatsapp_url) {
            toastWaAction.classList.remove('hidden');
            if (toastWaLink) toastWaLink.href = data.whatsapp_url;
          }
        }

        form.reset();
        document.getElementById('form-clinic-type').value = payload.clinic_type;
        window.switchClinicBooking(payload.clinic_type);

        toast.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        alert(data.message || 'Something went wrong. Please call the clinic directly.');
      }
    })
    .catch(err => {
      submitBtn.disabled = false;
      submitBtnText.textContent = originalText;
      console.error('Booking request error:', err);
      alert('Network issue. Please reach us directly on WhatsApp at +91 98765 43210.');
    });
  };


  // -------------------------------------------------------------
  // 6. MOBILE DRAWER NAVIGATION
  // -------------------------------------------------------------
  const drawer = document.getElementById('mobile-drawer');
  const drawerSheet = document.getElementById('mobile-drawer-sheet');
  const openBtn = document.getElementById('mobile-menu-open');
  const closeBtn = document.getElementById('mobile-menu-close');
  const backdrop = document.getElementById('mobile-drawer-backdrop');

  function openMobileDrawer() {
    if (!drawer || !drawerSheet) return;
    drawer.classList.remove('pointer-events-none');
    drawer.classList.remove('opacity-0');
    drawer.classList.add('opacity-100');
    drawerSheet.classList.remove('translate-x-full');
    drawerSheet.classList.add('translate-x-0');
  }

  function closeMobileDrawer() {
    if (!drawer || !drawerSheet) return;
    drawerSheet.classList.remove('translate-x-0');
    drawerSheet.classList.add('translate-x-full');
    drawer.classList.remove('opacity-100');
    drawer.classList.add('opacity-0');
    setTimeout(() => {
      drawer.classList.add('pointer-events-none');
    }, 300);
  }

  if (openBtn) openBtn.addEventListener('click', openMobileDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeMobileDrawer);
  if (backdrop) backdrop.addEventListener('click', closeMobileDrawer);

  window.openMobileDrawer = openMobileDrawer;
  window.closeMobileDrawer = closeMobileDrawer;


  // -------------------------------------------------------------
  // 7. KEYBOARD ESCAPE TO CLOSE MODAL
  // -------------------------------------------------------------
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      window.closeBookingModal();
      closeMobileDrawer();
    }
  });


  // -------------------------------------------------------------
  // 8. STICKY HEADER SCROLL BLUR ENHANCEMENT
  // -------------------------------------------------------------
  const siteHeader = document.getElementById('site-header');
  window.addEventListener('scroll', function () {
    if (!siteHeader) return;
    if (window.scrollY > 20) {
      siteHeader.classList.add('bg-white/90', 'shadow-md', 'border-slate-100');
      siteHeader.classList.remove('bg-white/70', 'border-transparent');
    } else {
      siteHeader.classList.remove('bg-white/90', 'shadow-md', 'border-slate-100');
      siteHeader.classList.add('bg-white/70', 'border-transparent');
    }
  }, { passive: true });


  // -------------------------------------------------------------
  // 9. INITIALIZE ON DOM CONTENT LOADED
  // -------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    setupBookingButtonInterceptors();

    // Set today's date as min for date input
    const dateInput = document.getElementById('preferred-date');
    if (dateInput) {
      const today = new Date().toISOString().split('T')[0];
      dateInput.min = today;
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      dateInput.value = tomorrow.toISOString().split('T')[0];
    }

    const modalDate = document.getElementById('modal-preferred-date');
    if (modalDate) {
      const today = new Date().toISOString().split('T')[0];
      modalDate.min = today;
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      modalDate.value = tomorrow.toISOString().split('T')[0];
    }

    // Detect initial clinic from page route or hidden input
    const formClinicInput = document.getElementById('form-clinic-type');
    let initType = 'dental';
    if (window.location.pathname.includes('pediatric')) {
      initType = 'pediatric';
    } else if (formClinicInput && formClinicInput.value) {
      initType = formClinicInput.value;
    }

    if (document.getElementById('booking-wrapper')) {
      window.switchClinicBooking(initType);
    }

    // Handle hash on load (e.g. /#booking-wrapper)
    if (window.location.hash === '#booking-wrapper') {
      setTimeout(() => {
        window.scrollToBooking(initType);
      }, 350);
    }
  });

})();