/**
 * Roots Dental Clinic & Buds Child Clinic — Interactive Medical Sanctuary Engine
 * Features:
 *  1. Progressive 3-Step Slide-Through Booking Engine (In-Page & Mobile Modal)
 *     - Step 1: "Who is the appointment for?" (Name, Clinic & Service)
 *     - Step 2: "When should we schedule?" (Interactive Date & Time Slot)
 *     - Step 3: "How can we reach you?" (WhatsApp Mobile with Numeric Keypad Trigger)
 *  2. Clean Editorial Doctor Identity Machine (Zero Cluttered Floating Badges)
 *  3. Minimalist SVG Iconography (Zero Childish Native Emojis)
 *  4. Native Mobile Touch App UX with Instant Zero-Scroll Modals
 *  5. Direct Django AJAX Integration (/api/book/) with WhatsApp Routing
 */

(function () {
  'use strict';

  // Curated Medical Datasets
  const DENTAL_SERVICES = [
    'General Dentistry & Oral Assessment',
    'Root Canal Treatment (Single-Visit Rotary)',
    'Clear Aligners & Orthodontic Simulation',
    'Porcelain Veneers & Smile Makeover',
    'Permanent Dental Implants (Titanium)',
    'Pediatric Dental Care (Kids Dentistry)',
    'Gum Therapy & Laser Periodontics',
    'Emergency Toothache & Trauma Relief'
  ];

  const PEDIATRIC_SERVICES = [
    'Newborn Intensive Assessment & Jaundice',
    'Complete IAP Immunization & Cold-Chain',
    'Developmental Milestones & Growth Check',
    'Acute Childhood Illnesses & Fever Care',
    'Infant Nutrition & Lactation Consultation',
    'Pediatric Allergy, Asthma & Respiratory',
    'Behavioral & Learning Milestones Guide',
    'Adolescent Health & Wellness Review'
  ];

  let currentClinic = 'dental';
  let inPageStep = 1;
  let modalStep = 1;

  // -------------------------------------------------------------
  // 1. PROGRESSIVE STEPPER: IN-PAGE BOOKING ENGINE (#booking-wrapper)
  // -------------------------------------------------------------
  window.goToBookingStep = function (step) {
    // Clear any previous error badges
    const existingErr = document.getElementById('patient-name-error');
    if (existingErr) existingErr.remove();
    const existingDateErr = document.getElementById('preferred-date-error');
    if (existingDateErr) existingDateErr.remove();

    // Validate current step before advancing
    if (step > inPageStep) {
      if (inPageStep === 1) {
        const nameInput = document.getElementById('patient-name');
        if (!nameInput || !nameInput.value.trim()) {
          if (nameInput) {
            nameInput.focus();
            nameInput.classList.remove('animate-shake');
            void nameInput.offsetWidth;
            nameInput.classList.add('animate-shake', 'border-rose-500', 'ring-2', 'ring-rose-200');

            const errDiv = document.createElement('div');
            errDiv.id = 'patient-name-error';
            errDiv.className = 'flex items-center gap-1.5 text-xs font-semibold text-rose-600 mt-2 bg-rose-50 border border-rose-200 px-3.5 py-2 rounded-xl animate-shake';
            errDiv.innerHTML = '<svg class="w-4 h-4 text-rose-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg><span>Please enter the patient\'s full name to continue</span>';
            const parent = nameInput.closest('.relative') ? nameInput.closest('.relative').parentElement : nameInput.parentElement;
            parent.appendChild(errDiv);

            nameInput.addEventListener('input', function onInputClear() {
              if (nameInput.value.trim()) {
                const err = document.getElementById('patient-name-error');
                if (err) err.remove();
                nameInput.classList.remove('border-rose-500', 'ring-2', 'ring-rose-200');
                nameInput.removeEventListener('input', onInputClear);
              }
            });

            setTimeout(() => {
              nameInput.classList.remove('border-rose-500', 'ring-2', 'ring-rose-200', 'animate-shake');
            }, 3000);
          }
          return;
        }
      }
      if (inPageStep === 2) {
        const dateInput = document.getElementById('preferred-date');
        if (!dateInput || !dateInput.value) {
          if (dateInput) {
            dateInput.focus();
            dateInput.classList.remove('animate-shake');
            void dateInput.offsetWidth;
            dateInput.classList.add('animate-shake', 'border-rose-500', 'ring-2', 'ring-rose-200');

            const errDiv = document.createElement('div');
            errDiv.id = 'preferred-date-error';
            errDiv.className = 'flex items-center gap-1.5 text-xs font-semibold text-rose-600 mt-2 bg-rose-50 border border-rose-200 px-3.5 py-2 rounded-xl animate-shake';
            errDiv.innerHTML = '<svg class="w-4 h-4 text-rose-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg><span>Please choose your preferred appointment date</span>';
            const parent = dateInput.closest('.relative') ? dateInput.closest('.relative').parentElement : dateInput.parentElement;
            parent.appendChild(errDiv);

            setTimeout(() => {
              dateInput.classList.remove('border-rose-500', 'ring-2', 'ring-rose-200', 'animate-shake');
            }, 3000);
          }
          return;
        }
      }
    }

    inPageStep = step;

    // Panes
    const step1Pane = document.getElementById('booking-step-1');
    const step2Pane = document.getElementById('booking-step-2');
    const step3Pane = document.getElementById('booking-step-3');

    if (step1Pane) {
      step1Pane.classList.toggle('hidden-step', step !== 1);
      step1Pane.classList.toggle('active-step', step === 1);
      step1Pane.style.display = (step === 1 ? 'block' : 'none');
    }
    if (step2Pane) {
      step2Pane.classList.toggle('hidden-step', step !== 2);
      step2Pane.classList.toggle('active-step', step === 2);
      step2Pane.style.display = (step === 2 ? 'block' : 'none');
    }
    if (step3Pane) {
      step3Pane.classList.toggle('hidden-step', step !== 3);
      step3Pane.classList.toggle('active-step', step === 3);
      step3Pane.style.display = (step === 3 ? 'block' : 'none');
    }

    // Step Indicator Pills
    for (let i = 1; i <= 3; i++) {
      const pill = document.getElementById(`booking-step-indicator-${i}`);
      const text = document.getElementById(`booking-step-text-${i}`);
      if (pill) {
        if (i < step) {
          pill.className = 'w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold bg-emerald-600 text-white cursor-pointer';
          pill.innerHTML = '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>';
        } else if (i === step) {
          pill.className = currentClinic === 'dental' 
            ? 'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold bg-dental-600 text-white shadow-sm cursor-pointer'
            : 'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold bg-pediatric-600 text-white shadow-sm cursor-pointer';
          pill.textContent = i;
        } else {
          pill.className = 'w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium bg-slate-100 text-slate-400 cursor-pointer';
          pill.textContent = i;
        }
      }
      if (text) {
        text.className = (i === step) 
          ? 'text-xs font-heading font-semibold text-slate-900 hidden sm:inline cursor-pointer'
          : 'text-xs font-heading text-slate-400 hidden sm:inline cursor-pointer';
      }
    }

    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  };

  // Select Time Slot Pill
  window.selectTimeSlot = function (timeSlot, isModal = false) {
    const inputId = isModal ? 'modal-preferred-time' : 'preferred-time';
    const hiddenInput = document.getElementById(inputId);
    if (hiddenInput) hiddenInput.value = timeSlot;

    const prefix = isModal ? 'modal-slot-' : 'slot-';
    const slots = ['morning', 'afternoon', 'evening'];
    slots.forEach(s => {
      const btn = document.getElementById(prefix + s);
      if (btn) {
        const matches = btn.getAttribute('data-value') === timeSlot;
        if (matches) {
          btn.className = (currentClinic === 'dental')
            ? 'flex-1 py-3 px-3 rounded-2xl text-xs font-heading font-bold text-center border-2 border-dental-600 bg-dental-50 text-dental-700 shadow-sm transition'
            : 'flex-1 py-3 px-3 rounded-2xl text-xs font-heading font-bold text-center border-2 border-pediatric-600 bg-pediatric-50 text-pediatric-700 shadow-sm transition';
        } else {
          btn.className = 'flex-1 py-3 px-3 rounded-2xl text-xs font-heading font-medium text-center border border-slate-200 bg-white text-slate-600 hover:border-slate-300 transition';
        }
      }
    });
  };

  // -------------------------------------------------------------
  // 2. MORPHING IN-PAGE CLINIC SWITCHER WITH SMOOTH CROSSFADE
  // -------------------------------------------------------------
  window.switchClinicBooking = function (type, preselectedService) {
    currentClinic = type;

    const formClinicInput = document.getElementById('form-clinic-type');
    const dentalLayer = document.getElementById('panel-layer-dental');
    const pediatricLayer = document.getElementById('panel-layer-pediatric');
    const togglePill = document.getElementById('clinic-toggle-pill');
    const btnDental = document.getElementById('btn-toggle-dental');
    const btnPediatric = document.getElementById('btn-toggle-pediatric');
    const mobileAvatar = document.getElementById('mobile-pill-avatar');
    const mobilePillName = document.getElementById('mobile-pill-name');
    const mobilePillDesc = document.getElementById('mobile-pill-desc');
    const mobilePill = document.getElementById('mobile-doctor-pill');
    const parentNameGroup = document.getElementById('parent-name-group');
    const inputParent = document.getElementById('parent-name');
    const labelPatient = document.getElementById('label-patient-name');
    const inputPatient = document.getElementById('patient-name');
    const serviceSelect = document.getElementById('service-needed');
    const submitBtn = document.getElementById('btn-submit-booking');
    const submitBtnText = document.getElementById('submit-btn-text');

    if (formClinicInput) formClinicInput.value = type;

    // 1. Crossfade Left Doctor Presentation Layers with Smooth Spring Effect
    if (dentalLayer && pediatricLayer) {
      if (type === 'dental') {
        dentalLayer.classList.remove('is-inactive');
        dentalLayer.classList.add('is-active');
        pediatricLayer.classList.remove('is-active');
        pediatricLayer.classList.add('is-inactive');
      } else {
        pediatricLayer.classList.remove('is-inactive');
        pediatricLayer.classList.add('is-active');
        dentalLayer.classList.remove('is-active');
        dentalLayer.classList.add('is-inactive');
      }
    }

    // 2. Smooth Toggle Switch Pill Slide
    if (togglePill) {
      if (type === 'dental') {
        togglePill.classList.remove('pill-pediatric');
        togglePill.classList.add('pill-dental');
      } else {
        togglePill.classList.remove('pill-dental');
        togglePill.classList.add('pill-pediatric');
      }
    }

    // 3. Smooth Mobile Pill Banner Fade
    if (mobilePill) {
      mobilePill.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
      mobilePill.style.opacity = '0.5';
      mobilePill.style.transform = 'scale(0.98)';
      setTimeout(() => {
        if (type === 'dental') {
          if (mobileAvatar) mobileAvatar.src = '/static/images/dentist_sabina.png';
          if (mobilePillName) mobilePillName.textContent = 'Dr. Sabina Firoj Shaikh';
          if (mobilePillDesc) mobilePillDesc.textContent = 'B.D.S, M.D.S (Gold Medalist) • Conservative Dentistry & Endodontics';
        } else {
          if (mobileAvatar) mobileAvatar.src = '/static/images/pediatrician_jalil.png';
          if (mobilePillName) mobilePillName.textContent = 'Dr. Jalil S. Mujawar';
          if (mobilePillDesc) mobilePillDesc.textContent = 'MBBS, DNB(Pediatrics), MNAMS • Pediatrician & Neonatologist';
        }
        mobilePill.style.opacity = '1';
        mobilePill.style.transform = 'scale(1)';
      }, 120);
    }

    if (type === 'dental') {
      if (btnDental) {
        btnDental.className = 'relative z-10 flex-1 py-2.5 px-4 rounded-xl font-heading font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all duration-300 text-dental-800 cursor-pointer';
      }
      if (btnPediatric) {
        btnPediatric.className = 'relative z-10 flex-1 py-2.5 px-4 rounded-xl font-heading font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all duration-300 text-slate-500 hover:text-slate-900 cursor-pointer';
      }

      if (labelPatient) labelPatient.textContent = 'Patient Full Name';
      if (inputPatient) inputPatient.placeholder = 'e.g. Rahul Kulkarni';
      if (parentNameGroup) {
        parentNameGroup.classList.add('hidden');
        if (inputParent) inputParent.removeAttribute('required');
      }

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

      // Slot buttons for Roots Dental Clinic Hours
      const slotMorning = document.getElementById('slot-morning');
      const slotEvening = document.getElementById('slot-evening');
      const slotAfternoon = document.getElementById('slot-afternoon');
      const smTitle = document.getElementById('slot-morning-title');
      const smTime = document.getElementById('slot-morning-time');
      const seTitle = document.getElementById('slot-evening-title');
      const seTime = document.getElementById('slot-evening-time');
      const spTitle = document.getElementById('slot-special-title');
      const spTime = document.getElementById('slot-special-time');

      if (slotMorning) slotMorning.setAttribute('data-value', 'Morning (11:00 AM - 2:00 PM)');
      if (smTitle) smTitle.textContent = 'Morning';
      if (smTime) smTime.textContent = '11:00 AM – 2:00 PM';

      if (slotEvening) slotEvening.setAttribute('data-value', 'Evening (6:00 PM - 8:30 PM)');
      if (seTitle) seTitle.textContent = 'Evening';
      if (seTime) seTime.textContent = '6:00 PM – 8:30 PM';

      if (slotAfternoon) slotAfternoon.setAttribute('data-value', 'Sunday (By Appointment)');
      if (spTitle) spTitle.textContent = 'Sunday';
      if (spTime) spTime.textContent = 'By Appointment';

      window.selectTimeSlot('Morning (11:00 AM - 2:00 PM)', false);

      if (submitBtn) {
        submitBtn.className = 'w-full py-4 px-6 rounded-2xl font-heading font-bold text-sm text-white bg-dental-600 hover:bg-dental-700 shadow-lg shadow-dental-700/20 active:scale-98 transition flex items-center justify-center gap-2 cursor-pointer';
      }
      if (submitBtnText) submitBtnText.textContent = 'Confirm & Request Dental Consultation';

    } else {
      if (btnDental) {
        btnDental.className = 'relative z-10 flex-1 py-2.5 px-4 rounded-xl font-heading font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all duration-300 text-slate-500 hover:text-slate-900 cursor-pointer';
      }
      if (btnPediatric) {
        btnPediatric.className = 'relative z-10 flex-1 py-2.5 px-4 rounded-xl font-heading font-bold text-xs sm:text-sm flex items-center justify-center gap-2 transition-all duration-300 text-pediatric-800 cursor-pointer';
      }

      if (labelPatient) labelPatient.textContent = "Child's Full Name";
      if (inputPatient) inputPatient.placeholder = 'e.g. Aarav Mehta (4 yrs)';
      if (parentNameGroup) {
        parentNameGroup.classList.remove('hidden');
        if (inputParent) inputParent.setAttribute('required', 'required');
      }

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

      // Slot buttons for Buds Child Clinic Hours
      const slotMorning = document.getElementById('slot-morning');
      const slotEvening = document.getElementById('slot-evening');
      const slotAfternoon = document.getElementById('slot-afternoon');
      const smTitle = document.getElementById('slot-morning-title');
      const smTime = document.getElementById('slot-morning-time');
      const seTitle = document.getElementById('slot-evening-title');
      const seTime = document.getElementById('slot-evening-time');
      const spTitle = document.getElementById('slot-special-title');
      const spTime = document.getElementById('slot-special-time');

      if (slotMorning) slotMorning.setAttribute('data-value', 'Sat Morning (10:00 AM - 1:00 PM)');
      if (smTitle) smTitle.textContent = 'Sat Morning';
      if (smTime) smTime.textContent = '10:00 AM – 1:00 PM';

      if (slotEvening) slotEvening.setAttribute('data-value', 'Evening (5:30 PM - 8:30 PM)');
      if (seTitle) seTitle.textContent = 'Mon–Sat Evening';
      if (seTime) seTime.textContent = '5:30 PM – 8:30 PM';

      if (slotAfternoon) slotAfternoon.setAttribute('data-value', 'Sunday (By Appointment)');
      if (spTitle) spTitle.textContent = 'Sunday';
      if (spTime) spTime.textContent = 'By Appointment';

      window.selectTimeSlot('Evening (5:30 PM - 8:30 PM)', false);

      if (submitBtn) {
        submitBtn.className = 'w-full py-4 px-6 rounded-2xl font-heading font-bold text-sm text-white bg-pediatric-600 hover:bg-pediatric-700 shadow-lg shadow-pediatric-700/20 active:scale-98 transition flex items-center justify-center gap-2 cursor-pointer';
      }
      if (submitBtnText) submitBtnText.textContent = 'Confirm & Request Child Care Appointment';
    }

    window.goToBookingStep(inPageStep);
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  };


  // -------------------------------------------------------------
  // 3. PROGRESSIVE STEPPER: MOBILE & DESKTOP MODAL BOOKING SHEET
  // -------------------------------------------------------------
  window.goToModalStep = function (step) {
    const existingErr = document.getElementById('modal-patient-name-error');
    if (existingErr) existingErr.remove();
    const existingDateErr = document.getElementById('modal-preferred-date-error');
    if (existingDateErr) existingDateErr.remove();

    if (step > modalStep) {
      if (modalStep === 1) {
        const nameInput = document.getElementById('modal-patient-name');
        if (!nameInput || !nameInput.value.trim()) {
          if (nameInput) {
            nameInput.focus();
            nameInput.classList.remove('animate-shake');
            void nameInput.offsetWidth;
            nameInput.classList.add('animate-shake', 'border-rose-500', 'ring-2', 'ring-rose-200');

            const errDiv = document.createElement('div');
            errDiv.id = 'modal-patient-name-error';
            errDiv.className = 'flex items-center gap-1.5 text-xs font-semibold text-rose-600 mt-1.5 bg-rose-50 border border-rose-200 px-3 py-1.5 rounded-xl animate-shake';
            errDiv.innerHTML = '<svg class="w-3.5 h-3.5 text-rose-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg><span>Please enter the patient\'s name to continue</span>';
            const parent = nameInput.parentElement;
            parent.appendChild(errDiv);

            nameInput.addEventListener('input', function onInputClear() {
              if (nameInput.value.trim()) {
                const err = document.getElementById('modal-patient-name-error');
                if (err) err.remove();
                nameInput.classList.remove('border-rose-500', 'ring-2', 'ring-rose-200');
                nameInput.removeEventListener('input', onInputClear);
              }
            });

            setTimeout(() => {
              nameInput.classList.remove('border-rose-500', 'ring-2', 'ring-rose-200', 'animate-shake');
            }, 3000);
          }
          return;
        }
      }
      if (modalStep === 2) {
        const dateInput = document.getElementById('modal-preferred-date');
        if (!dateInput || !dateInput.value) {
          if (dateInput) {
            dateInput.focus();
            dateInput.classList.add('animate-shake', 'border-rose-500');
            setTimeout(() => dateInput.classList.remove('animate-shake', 'border-rose-500'), 2000);
          }
          return;
        }
      }
    }

    modalStep = step;

    const step1Pane = document.getElementById('modal-step-1');
    const step2Pane = document.getElementById('modal-step-2');
    const step3Pane = document.getElementById('modal-step-3');

    if (step1Pane) {
      step1Pane.classList.toggle('hidden-step', step !== 1);
      step1Pane.classList.toggle('active-step', step === 1);
      step1Pane.style.display = (step === 1 ? 'block' : 'none');
    }
    if (step2Pane) {
      step2Pane.classList.toggle('hidden-step', step !== 2);
      step2Pane.classList.toggle('active-step', step === 2);
      step2Pane.style.display = (step === 2 ? 'block' : 'none');
    }
    if (step3Pane) {
      step3Pane.classList.toggle('hidden-step', step !== 3);
      step3Pane.classList.toggle('active-step', step === 3);
      step3Pane.style.display = (step === 3 ? 'block' : 'none');
    }

    // Modal Step Indicator
    for (let i = 1; i <= 3; i++) {
      const pill = document.getElementById(`modal-step-indicator-${i}`);
      const text = document.getElementById(`modal-step-text-${i}`);
      if (pill) {
        if (i < step) {
          pill.className = 'w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-semibold bg-emerald-600 text-white cursor-pointer';
          pill.innerHTML = '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>';
        } else if (i === step) {
          pill.className = currentClinic === 'dental'
            ? 'w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold bg-dental-600 text-white shadow-xs cursor-pointer'
            : 'w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold bg-pediatric-600 text-white shadow-xs cursor-pointer';
          pill.textContent = i;
        } else {
          pill.className = 'w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-medium bg-slate-100 text-slate-400 cursor-pointer';
          pill.textContent = i;
        }
      }
      if (text) {
        text.className = (i === step)
          ? 'text-[11px] font-heading font-semibold text-slate-800 cursor-pointer'
          : 'text-[11px] font-heading text-slate-400 cursor-pointer';
      }
    }

    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  };

  window.setModalClinic = function (type) {
    const modalClinicInput = document.getElementById('modal-clinic-type');
    const btnDental = document.getElementById('modal-toggle-dental');
    const btnPediatric = document.getElementById('modal-toggle-pediatric');
    const avatar = document.getElementById('modal-doctor-avatar');
    const name = document.getElementById('modal-doctor-name');
    const desc = document.getElementById('modal-doctor-desc');
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
        btnPediatric.className = 'flex-1 py-2 px-3 rounded-xl font-heading font-medium text-xs flex items-center justify-center gap-1.5 transition-all text-slate-500 hover:text-slate-800';
      }

      if (avatar) avatar.src = '/static/images/dentist_sabina.png';
      if (name) name.textContent = 'Dr. Sabina Firoj Shaikh';
      if (desc) desc.textContent = 'B.D.S, M.D.S (Gold Medalist) • Conservative Dentistry & Endodontics';

      // Update Modal Slots for Dental
      const mSlotMorning = document.getElementById('modal-slot-morning');
      const mSlotEvening = document.getElementById('modal-slot-evening');
      const mSlotAfternoon = document.getElementById('modal-slot-afternoon');
      if (mSlotMorning) {
        mSlotMorning.setAttribute('data-value', 'Morning (11:00 AM - 2:00 PM)');
        mSlotMorning.innerHTML = 'Morning<br><span class="text-[9px] font-normal text-slate-500">11am–2pm</span>';
      }
      if (mSlotEvening) {
        mSlotEvening.setAttribute('data-value', 'Evening (6:00 PM - 8:30 PM)');
        mSlotEvening.innerHTML = 'Evening<br><span class="text-[9px] font-normal text-slate-500">6pm–8:30pm</span>';
      }
      if (mSlotAfternoon) {
        mSlotAfternoon.setAttribute('data-value', 'Sunday (By Appointment)');
        mSlotAfternoon.innerHTML = 'Sunday<br><span class="text-[9px] font-normal text-slate-500">By Appt</span>';
      }
      window.selectTimeSlot('Morning (11:00 AM - 2:00 PM)', true);

      if (labelPatient) labelPatient.textContent = 'Patient Full Name';
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
        submitBtn.className = 'w-full py-3.5 px-5 rounded-2xl font-heading font-bold text-xs sm:text-sm text-white bg-dental-600 hover:bg-dental-700 shadow-lg shadow-dental-700/20 active:scale-98 transition flex items-center justify-center gap-2 cursor-pointer';
      }
      if (submitText) submitText.textContent = 'Request Dental Consultation';

    } else {
      if (btnDental) {
        btnDental.className = 'flex-1 py-2 px-3 rounded-xl font-heading font-medium text-xs flex items-center justify-center gap-1.5 transition-all text-slate-500 hover:text-slate-800';
      }
      if (btnPediatric) {
        btnPediatric.className = 'flex-1 py-2 px-3 rounded-xl font-heading font-bold text-xs flex items-center justify-center gap-1.5 transition-all bg-white text-pediatric-700 shadow-sm';
      }

      if (avatar) avatar.src = '/static/images/pediatrician_jalil.png';
      if (name) name.textContent = 'Dr. Jalil S. Mujawar';
      if (desc) desc.textContent = 'MBBS, DNB(Pediatrics), MNAMS • Pediatrician & Neonatologist';

      // Update Modal Slots for Pediatric
      const mSlotMorning = document.getElementById('modal-slot-morning');
      const mSlotEvening = document.getElementById('modal-slot-evening');
      const mSlotAfternoon = document.getElementById('modal-slot-afternoon');
      if (mSlotMorning) {
        mSlotMorning.setAttribute('data-value', 'Sat Morning (10:00 AM - 1:00 PM)');
        mSlotMorning.innerHTML = 'Sat Morning<br><span class="text-[9px] font-normal text-slate-500">10am–1pm</span>';
      }
      if (mSlotEvening) {
        mSlotEvening.setAttribute('data-value', 'Evening (5:30 PM - 8:30 PM)');
        mSlotEvening.innerHTML = 'Evening<br><span class="text-[9px] font-normal text-slate-500">5:30–8:30pm</span>';
      }
      if (mSlotAfternoon) {
        mSlotAfternoon.setAttribute('data-value', 'Sunday (By Appointment)');
        mSlotAfternoon.innerHTML = 'Sunday<br><span class="text-[9px] font-normal text-slate-500">By Appt</span>';
      }
      window.selectTimeSlot('Evening (5:30 PM - 8:30 PM)', true);

      if (labelPatient) labelPatient.textContent = "Child's Full Name";
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
        submitBtn.className = 'w-full py-3.5 px-5 rounded-2xl font-heading font-bold text-xs sm:text-sm text-white bg-pediatric-600 hover:bg-pediatric-700 shadow-lg shadow-pediatric-700/20 active:scale-98 transition flex items-center justify-center gap-2 cursor-pointer';
      }
      if (submitText) submitText.textContent = 'Request Child Care Consultation';
    }

    window.goToModalStep(modalStep);
  };

  // Open & Close Modal Sheet (Desktop & Mobile Universal Lightbox)
  window.openBookingModal = function (targetClinic, serviceName) {
    try {
      const modal = document.getElementById('mobile-booking-modal');
      const sheet = document.getElementById('modal-sheet');
      if (!modal || !sheet) {
        console.warn('Booking modal elements not found in DOM.');
        return;
      }

      let clinicToSet = targetClinic;
      if (!clinicToSet || (clinicToSet !== 'dental' && clinicToSet !== 'pediatric')) {
        clinicToSet = window.location.pathname.includes('pediatric') ? 'pediatric' : 'dental';
      }

      window.setModalClinic(clinicToSet);

      if (serviceName) {
        const selectService = document.getElementById('modal-service-needed');
        if (selectService) {
          for (let i = 0; i < selectService.options.length; i++) {
            const opt = selectService.options[i];
            if (opt.value.toLowerCase().includes(serviceName.toLowerCase()) || serviceName.toLowerCase().includes(opt.value.toLowerCase())) {
              opt.selected = true;
              break;
            }
          }
        }
      }

      window.goToModalStep(1);

      // Pre-set tomorrow date if empty
      const modalDate = document.getElementById('modal-preferred-date');
      if (modalDate && !modalDate.value) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        modalDate.value = tomorrow.toISOString().split('T')[0];
        modalDate.min = new Date().toISOString().split('T')[0];
      }

      // Show modal immediately
      modal.style.display = 'flex';
      modal.style.pointerEvents = 'auto';
      modal.classList.remove('pointer-events-none', 'opacity-0');
      modal.classList.add('opacity-100');

      // Animate sheet smoothly
      sheet.style.transform = (window.innerWidth >= 640) ? 'scale(1)' : 'translateY(0)';
      sheet.classList.remove('translate-y-full', 'sm:scale-95');
      sheet.classList.add('translate-y-0', 'sm:scale-100');

      document.body.style.overflow = 'hidden';

      // Focus patient name input
      setTimeout(() => {
        const nameInput = document.getElementById('modal-patient-name');
        if (nameInput) nameInput.focus();
      }, 100);

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

      sheet.style.transform = (window.innerWidth >= 640) ? 'scale(0.95)' : 'translateY(100%)';
      sheet.classList.remove('translate-y-0', 'sm:scale-100');
      sheet.classList.add('translate-y-full', 'sm:scale-95');

      modal.classList.remove('opacity-100');
      modal.classList.add('opacity-0', 'pointer-events-none');

      setTimeout(() => {
        modal.style.display = 'none';
        modal.style.pointerEvents = 'none';
        document.body.style.overflow = '';
      }, 250);
    } catch (err) {
      console.error('Error in closeBookingModal:', err);
    }
  };


  // -------------------------------------------------------------
  // 4. MODAL BOOKING SUBMISSION (/api/book/)
  // -------------------------------------------------------------
  window.handleModalBookingSubmit = function (e) {
    e.preventDefault();

    const submitBtn = document.getElementById('modal-submit-btn');
    const submitText = document.getElementById('modal-submit-text');
    const toast = document.getElementById('modal-toast');
    const toastMsg = document.getElementById('modal-toast-msg');
    const toastWa = document.getElementById('modal-toast-wa');
    const toastWaLink = document.getElementById('modal-toast-wa-link');

    const phoneVal = (document.getElementById('modal-phone-number')?.value || '').replace(/\D/g, '');
    const payload = {
      clinic_type: document.getElementById('modal-clinic-type').value,
      patient_name: document.getElementById('modal-patient-name').value.trim(),
      parent_name: (document.getElementById('modal-parent-name') ? document.getElementById('modal-parent-name').value.trim() : ''),
      phone_number: phoneVal,
      service_needed: document.getElementById('modal-service-needed').value,
      preferred_date: document.getElementById('modal-preferred-date').value,
      preferred_time: document.getElementById('modal-preferred-time').value,
      notes: ''
    };

    if (!payload.patient_name || payload.phone_number.length < 10 || !payload.preferred_date) {
      alert('Please provide your full name and a valid 10-digit WhatsApp number.');
      return;
    }

    const originalText = submitText ? submitText.textContent : 'Request Consultation';
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
            toastMsg.textContent = `Hello ${data.patient_name}, your consultation request is locked in! Our front desk is confirming your exact slot on WhatsApp.`;
          }
          if (toastWa && data.whatsapp_url) {
            toastWa.classList.remove('hidden');
            if (toastWaLink) toastWaLink.href = data.whatsapp_url;
          }
        }

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
      alert('Network issue. Reach us directly on WhatsApp at +91 99212 31399.');
    });
  };


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

    const phoneVal = (document.getElementById('phone-number')?.value || '').replace(/\D/g, '');
    const payload = {
      clinic_type: document.getElementById('form-clinic-type').value,
      patient_name: document.getElementById('patient-name').value.trim(),
      parent_name: (document.getElementById('parent-name') ? document.getElementById('parent-name').value.trim() : ''),
      phone_number: phoneVal,
      service_needed: document.getElementById('service-needed').value,
      preferred_date: document.getElementById('preferred-date').value,
      preferred_time: document.getElementById('preferred-time').value,
      notes: (document.getElementById('notes') ? document.getElementById('notes').value.trim() : '')
    };

    if (!payload.patient_name || payload.phone_number.length < 10 || !payload.preferred_date) {
      alert('Please fill out all required fields with a valid 10-digit WhatsApp phone number.');
      return;
    }

    const originalText = submitBtnText ? submitBtnText.textContent : 'Request Appointment';
    if (submitBtn) submitBtn.disabled = true;
    if (submitBtnText) submitBtnText.textContent = 'Reserving Your Slot...';

    fetch('/api/book/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      if (submitBtn) submitBtn.disabled = false;
      if (submitBtnText) submitBtnText.textContent = originalText;

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
        window.goToBookingStep(1);

        toast.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        alert(data.message || 'Something went wrong. Please call the clinic directly.');
      }
    })
    .catch(err => {
      if (submitBtn) submitBtn.disabled = false;
      if (submitBtnText) submitBtnText.textContent = originalText;
      console.error('Booking request error:', err);
      alert('Network issue. Reach us directly on WhatsApp at +91 99212 31399.');
    });
  };


  // -------------------------------------------------------------
  // 6. CONTEXTUAL ROUTING & IN-PAGE SCROLLING
  // -------------------------------------------------------------
  window.scrollToBooking = function (targetClinic, serviceName) {
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

      // Highlight patient name input so user immediately sees where to start
      setTimeout(() => {
        const patientInput = document.getElementById('patient-name');
        if (patientInput) {
          patientInput.focus();
          patientInput.classList.remove('animate-highlight-pulse');
          void patientInput.offsetWidth;
          patientInput.classList.add('animate-highlight-pulse');
          setTimeout(() => patientInput.classList.remove('animate-highlight-pulse'), 2500);
        }
      }, 350);
    } else {
      // If on About, Contact, Gallery, etc., open the booking modal directly!
      window.openBookingModal(targetClinic, serviceName);
    }
  };


  // -------------------------------------------------------------
  // 7. HEADER & NAVIGATION BUTTON INTERCEPTORS
  // -------------------------------------------------------------
  window.handleBookAppointmentClick = function (e) {
    if (e && e.preventDefault) e.preventDefault();
    const path = window.location.pathname;
    const clinic = path.includes('pediatric') ? 'pediatric' : 'dental';
    window.openBookingModal(clinic);
  };

  function setupBookingButtonInterceptors() {
    const headerBtn = document.getElementById('header-book-btn');
    const mobileBottomBtn = document.getElementById('mobile-bottom-book-btn');
    const mobileDrawerBtn = document.getElementById('mobile-drawer-book-btn');

    if (headerBtn) {
      headerBtn.onclick = window.handleBookAppointmentClick;
    }
    if (mobileBottomBtn) {
      mobileBottomBtn.onclick = function (e) {
        if (e && e.preventDefault) e.preventDefault();
        const path = window.location.pathname;
        const clinic = path.includes('pediatric') ? 'pediatric' : 'dental';
        window.openBookingModal(clinic);
      };
    }
    if (mobileDrawerBtn) {
      mobileDrawerBtn.onclick = function (e) {
        if (e && e.preventDefault) e.preventDefault();
        window.closeMobileDrawer();
        const path = window.location.pathname;
        const clinic = path.includes('pediatric') ? 'pediatric' : 'dental';
        setTimeout(() => {
          window.openBookingModal(clinic);
        }, 150);
      };
    }
  }


  // -------------------------------------------------------------
  // 8. MOBILE DRAWER NAVIGATION (BULLETPROOF ON-DEMAND LOOKUP)
  // -------------------------------------------------------------
  window.openMobileDrawer = function () {
    const drawer = document.getElementById('mobile-drawer');
    const drawerSheet = document.getElementById('mobile-drawer-sheet');
    if (!drawer || !drawerSheet) return;
    drawer.style.display = 'block';
    drawer.style.pointerEvents = 'auto';
    drawer.classList.remove('pointer-events-none', 'opacity-0');
    drawer.classList.add('opacity-100');
    drawerSheet.style.transform = 'translateX(0)';
    drawerSheet.classList.remove('translate-x-full');
    drawerSheet.classList.add('translate-x-0');
    document.body.style.overflow = 'hidden';
  };

  window.closeMobileDrawer = function () {
    const drawer = document.getElementById('mobile-drawer');
    const drawerSheet = document.getElementById('mobile-drawer-sheet');
    if (!drawer || !drawerSheet) return;
    drawerSheet.style.transform = 'translateX(100%)';
    drawerSheet.classList.remove('translate-x-0');
    drawerSheet.classList.add('translate-x-full');
    drawer.classList.remove('opacity-100');
    drawer.classList.add('opacity-0');
    setTimeout(() => {
      drawer.style.display = 'none';
      drawer.style.pointerEvents = 'none';
      drawer.classList.add('pointer-events-none');
      document.body.style.overflow = '';
    }, 250);
  };

  // Document-Level Delegation (Guarantees every button works immediately)
  document.addEventListener('click', function (e) {
    const openTrigger = e.target.closest('#mobile-menu-open');
    if (openTrigger) {
      e.preventDefault();
      window.openMobileDrawer();
      return;
    }
    const closeTrigger = e.target.closest('#mobile-menu-close, #mobile-drawer-backdrop');
    if (closeTrigger) {
      e.preventDefault();
      window.closeMobileDrawer();
      return;
    }
    const bookTrigger = e.target.closest('#header-book-btn');
    if (bookTrigger) {
      e.preventDefault();
      window.handleBookAppointmentClick(e);
      return;
    }
    const drawerBookTrigger = e.target.closest('#mobile-drawer-book-btn');
    if (drawerBookTrigger) {
      e.preventDefault();
      window.closeMobileDrawer();
      setTimeout(() => window.openBookingModal(), 150);
      return;
    }
    const bottomBookTrigger = e.target.closest('#mobile-bottom-book-btn');
    if (bottomBookTrigger) {
      e.preventDefault();
      window.openBookingModal();
      return;
    }
    const modalBackdrop = e.target.closest('#modal-backdrop');
    if (modalBackdrop) {
      e.preventDefault();
      window.closeBookingModal();
      return;
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      window.closeBookingModal();
      window.closeMobileDrawer();
    }
  });


  // -------------------------------------------------------------
  // 9. STICKY HEADER SCROLL BLUR ENHANCEMENT
  // -------------------------------------------------------------
  const siteHeader = document.getElementById('site-header');
  window.addEventListener('scroll', function () {
    if (!siteHeader) return;
    if (window.scrollY > 20) {
      siteHeader.classList.add('bg-white/95', 'shadow-sm', 'border-slate-100');
      siteHeader.classList.remove('bg-white/70', 'border-transparent');
    } else {
      siteHeader.classList.remove('bg-white/95', 'shadow-sm', 'border-slate-100');
      siteHeader.classList.add('bg-white/70', 'border-transparent');
    }
  }, { passive: true });


  // -------------------------------------------------------------
  // 10. INITIALIZATION
  // -------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    setupBookingButtonInterceptors();

    // Default dates
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

    // Initial clinic
    const formClinicInput = document.getElementById('form-clinic-type');
    let initType = 'dental';
    if (window.location.pathname.includes('pediatric')) {
      initType = 'pediatric';
    } else if (formClinicInput && formClinicInput.value) {
      initType = formClinicInput.value;
    }

    // Default time slots aligned to clinic consultation hours
    const defaultSlot = initType === 'dental' ? 'Morning (11:00 AM - 2:00 PM)' : 'Evening (5:30 PM - 8:30 PM)';
    window.selectTimeSlot(defaultSlot, false);
    window.selectTimeSlot(defaultSlot, true);

    if (document.getElementById('booking-wrapper')) {
      window.switchClinicBooking(initType);
      window.goToBookingStep(1);
    }

    if (window.location.hash === '#booking-wrapper') {
      setTimeout(() => {
        window.scrollToBooking(initType);
      }, 350);
    }

    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  });

})();
