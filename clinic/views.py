from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from datetime import datetime, timedelta
from .models import Doctor, Patient, Appointment, Treatment, Medication, MedicalRecord, UserRole, Clinic, TestReport, PathologyReport, Prescription, PharmacyInventory, PatentInvention
from .forms import (
    PatientRegistrationForm, DoctorRegistrationForm, AppointmentForm,
    TreatmentForm, MedicationForm, MedicalRecordForm, LoginForm,
    TestReportForm, PathologyReportForm, PrescriptionForm,
    DoctorProfileUpdateForm, PatientProfileUpdateForm, PatentInventionForm
)


def home(request):
    """Home page view"""
    clinic = Clinic.objects.first()
    doctors_count = Doctor.objects.filter(is_active=True).count()
    patients_count = Patient.objects.count()
    appointments_count = Appointment.objects.filter(status='confirmed').count()
    
    # Dashboard data for authenticated users
    total_appointments = Appointment.objects.count()
    in_progress_appointments = Appointment.objects.filter(status='confirmed').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    overdue_appointments = Appointment.objects.filter(status='pending').count()
    
    # Get total revenue from treatments
    from django.db.models import Sum, F
    total_revenue = Treatment.objects.aggregate(total=Sum(F('cost')))['total'] or 0
    
    # Get recent appointments
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:5]
    
    context = {
        'clinic': clinic,
        'doctors_count': doctors_count,
        'patients_count': patients_count,
        'appointments_count': appointments_count,
        'total_appointments': total_appointments,
        'in_progress_appointments': in_progress_appointments,
        'completed_appointments': completed_appointments,
        'overdue_appointments': overdue_appointments,
        'total_revenue': total_revenue,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'clinic/home.html', context)


def patient_register(request):
    """Patient registration view"""
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create patient profile
            Patient.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone'),
                date_of_birth=form.cleaned_data.get('date_of_birth'),
                gender=form.cleaned_data.get('gender'),
                address=form.cleaned_data.get('address'),
                city=form.cleaned_data.get('city'),
                postal_code=form.cleaned_data.get('postal_code'),
                emergency_contact=form.cleaned_data.get('emergency_contact'),
                emergency_contact_phone=form.cleaned_data.get('emergency_contact_phone'),
                blood_group=form.cleaned_data.get('blood_group', ''),
                allergies=form.cleaned_data.get('allergies', ''),
                medical_conditions=form.cleaned_data.get('medical_conditions', '')
            )
            
            # Create user role
            UserRole.objects.create(user=user, role='patient')
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'clinic/patient_register.html', {'form': form})


def doctor_register(request):
    """Doctor registration view"""
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create doctor profile
            Doctor.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone'),
                specialization=form.cleaned_data.get('specialization'),
                license_number=form.cleaned_data.get('license_number'),
                experience_years=form.cleaned_data.get('experience_years'),
                bio=form.cleaned_data.get('bio', ''),
                working_days=form.cleaned_data.get('working_days'),
                start_time=form.cleaned_data.get('start_time'),
                end_time=form.cleaned_data.get('end_time'),
                consultation_fee=form.cleaned_data.get('consultation_fee')
            )
            
            # Create user role
            UserRole.objects.create(user=user, role='doctor')
            
            messages.success(request, 'Doctor registration successful! Please login.')
            return redirect('login')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'clinic/doctor_register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Redirect based on user role
            try:
                role = user.role.role
                if role == 'doctor':
                    return redirect('doctor_dashboard')
                elif role == 'patient':
                    return redirect('patient_dashboard')
                else:
                    return redirect('dashboard')
            except:
                return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'clinic/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


@login_required(login_url='login')
def dashboard(request):
    """General dashboard"""
    try:
        role = request.user.role.role
        if role == 'doctor':
            return redirect('doctor_dashboard')
        elif role == 'patient':
            return redirect('patient_dashboard')
    except:
        pass
    
    return render(request, 'clinic/dashboard.html')


@login_required(login_url='login')
def patient_dashboard(request):
    """Patient dashboard with comprehensive medical information"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    upcoming_appointments = patient.appointments.filter(
        status='confirmed',
        appointment_date__gte=datetime.now().date()
    ).order_by('appointment_date', 'appointment_time')[:5]
    
    past_appointments = patient.appointments.filter(
        appointment_date__lt=datetime.now().date()
    ).order_by('-appointment_date')[:5]
    
    treatments = Treatment.objects.filter(appointment__patient=patient).select_related('appointment')[:5]
    
    medical_records = patient.medical_records.all().order_by('-date_created')[:5]
    
    test_reports = patient.test_reports.all().order_by('-test_date')[:5]
    
    pathology_reports = patient.pathology_reports.all().order_by('-report_date')[:5]
    
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-prescribed_date')[:5]
    
    # Calculate statistics
    total_appointments = patient.appointments.count()
    completed_treatments = Treatment.objects.filter(appointment__patient=patient, status='completed').count()
    pending_treatments = Treatment.objects.filter(appointment__patient=patient, status__in=['recommended', 'in_progress']).count()
    total_medical_records = patient.medical_records.count()
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'treatments': treatments,
        'medical_records': medical_records,
        'test_reports': test_reports,
        'pathology_reports': pathology_reports,
        'prescriptions': prescriptions,
        'total_appointments': total_appointments,
        'completed_treatments': completed_treatments,
        'pending_treatments': pending_treatments,
        'total_medical_records': total_medical_records,
    }
    
    return render(request, 'clinic/patient_dashboard.html', context)


@login_required(login_url='login')
def doctor_dashboard(request):
    """Doctor dashboard"""
    try:
        doctor = request.user.doctor
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    today = datetime.now().date()
    today_appointments = doctor.appointments.filter(
        appointment_date=today,
        status__in=['pending', 'confirmed']
    ).order_by('appointment_time')
    
    upcoming_appointments = doctor.appointments.filter(
        appointment_date__gte=today,
        status='confirmed'
    ).order_by('appointment_date', 'appointment_time')[:5]
    
    # Patent Statistics
    user_patents = PatentInvention.objects.filter(user=request.user)
    total_patents = user_patents.count()
    draft_patents = user_patents.filter(status='draft').count()
    submitted_patents = user_patents.filter(status='submitted').count()
    approved_patents = user_patents.filter(status='approved').count()
    granted_patents = user_patents.filter(status='granted').count()
    recent_patents = user_patents.order_by('-created_at')[:5]
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        # Patent data
        'total_patents': total_patents,
        'draft_patents': draft_patents,
        'submitted_patents': submitted_patents,
        'approved_patents': approved_patents,
        'granted_patents': granted_patents,
        'recent_patents': recent_patents,
        # Tooth lists for EDR charting
        'adult_upper': [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28],
        'adult_lower': [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38],
        'pediatric_upper': [55, 54, 53, 52, 51, 61, 62, 63, 64, 65],
        'pediatric_lower': [85, 84, 83, 82, 81, 71, 72, 73, 74, 75],
    }
    
    return render(request, 'clinic/doctor_dashboard.html', context)


@login_required(login_url='login')
def doctors_list(request):
    """List all doctors"""
    doctors = Doctor.objects.filter(is_active=True).select_related('user')
    specialization = request.GET.get('specialization')
    
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    context = {
        'doctors': doctors,
        'specializations': Doctor._meta.get_field('specialization').choices,
    }
    
    return render(request, 'clinic/doctors_list.html', context)


@login_required(login_url='login')
def doctor_profile(request, doctor_id):
    """Doctor profile view"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    appointments = doctor.appointments.filter(status='completed').count()
    
    context = {
        'doctor': doctor,
        'total_appointments': appointments,
    }
    
    return render(request, 'clinic/doctor_profile.html', context)


@login_required(login_url='login')
def my_profile(request):
    """User profile view"""
    try:
        patient = request.user.patient
        context = {'patient': patient, 'profile_type': 'patient'}
    except:
        try:
            doctor = request.user.doctor
            context = {'doctor': doctor, 'profile_type': 'doctor'}
        except:
            messages.error(request, 'Profile not found.')
            return redirect('home')
    
    return render(request, 'clinic/profile.html', context)


@login_required(login_url='login')
def book_appointment(request):
    """Book appointment"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.status = 'pending'
            appointment.save()
            
            messages.success(request, 'Appointment request submitted! Awaiting confirmation.')
            return redirect('patient_appointments')
    else:
        form = AppointmentForm()
    
    context = {'form': form}
    return render(request, 'clinic/book_appointment.html', context)


@login_required(login_url='login')
def patient_appointments(request):
    """Patient appointments list"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    appointments = patient.appointments.all().select_related('doctor').order_by('-appointment_date')
    
    context = {'appointments': appointments}
    return render(request, 'clinic/patient_appointments.html', context)


@login_required(login_url='login')
def appointment_detail(request, appointment_id):
    """Appointment detail view"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    try:
        patient = request.user.patient
        if appointment.patient != patient:
            messages.error(request, 'You do not have permission to view this appointment.')
            return redirect('home')
    except:
        try:
            doctor = request.user.doctor
            if appointment.doctor != doctor:
                messages.error(request, 'You do not have permission to view this appointment.')
                return redirect('home')
        except:
            messages.error(request, 'You do not have permission to view this appointment.')
            return redirect('home')
    
    context = {'appointment': appointment}
    return render(request, 'clinic/appointment_detail.html', context)


@login_required(login_url='login')
def cancel_appointment(request, appointment_id):
    """Cancel appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    try:
        patient = request.user.patient
        if appointment.patient != patient:
            messages.error(request, 'You do not have permission to cancel this appointment.')
            return redirect('home')
    except:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('home')
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('patient_appointments')
    
    context = {'appointment': appointment}
    return render(request, 'clinic/cancel_appointment.html', context)


@login_required(login_url='login')
def confirm_appointment(request, appointment_id):
    """Doctor confirms appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    try:
        doctor = request.user.doctor
        if appointment.doctor != doctor:
            messages.error(request, 'You do not have permission to confirm this appointment.')
            return redirect('home')
    except:
        messages.error(request, 'You do not have permission to confirm this appointment.')
        return redirect('home')
    
    if request.method == 'POST':
        appointment.status = 'confirmed'
        appointment.notes = request.POST.get('notes', '')
        appointment.save()
        messages.success(request, 'Appointment confirmed.')
        return redirect('doctor_appointments')
    
    context = {'appointment': appointment}
    return render(request, 'clinic/confirm_appointment.html', context)


@login_required(login_url='login')
def doctor_appointments(request):
    """Doctor appointments list"""
    try:
        doctor = request.user.doctor
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    appointments = doctor.appointments.all().select_related('patient').order_by('-appointment_date')
    
    context = {'appointments': appointments}
    return render(request, 'clinic/doctor_appointments.html', context)


@login_required(login_url='login')
def patient_treatments(request):
    """Patient treatments list"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    treatments = Treatment.objects.filter(appointment__patient=patient).select_related('appointment').order_by('-created_at')
    
    context = {'treatments': treatments}
    return render(request, 'clinic/patient_treatments.html', context)


@login_required(login_url='login')
def treatment_detail(request, treatment_id):
    """Treatment detail view"""
    treatment = get_object_or_404(Treatment, id=treatment_id)
    
    try:
        patient = request.user.patient
        if treatment.appointment.patient != patient:
            messages.error(request, 'You do not have permission to view this treatment.')
            return redirect('home')
    except:
        messages.error(request, 'You do not have permission to view this treatment.')
        return redirect('home')
    
    medications = treatment.medications.all()
    
    context = {
        'treatment': treatment,
        'medications': medications,
    }
    return render(request, 'clinic/treatment_detail.html', context)


@login_required(login_url='login')
def medical_records(request):
    """Medical records list"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    records = patient.medical_records.all().order_by('-date_created')
    
    context = {'records': records}
    return render(request, 'clinic/medical_records.html', context)


@login_required(login_url='login')
def add_medical_record(request):
    """Add medical record"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.save()
            messages.success(request, 'Medical record added successfully.')
            return redirect('medical_records')
    else:
        form = MedicalRecordForm()
    
    context = {'form': form}
    return render(request, 'clinic/add_medical_record.html', context)


@login_required(login_url='login')
def get_available_slots(request, doctor_id):
    """Get available appointment slots for a doctor"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    slots = doctor.get_available_slots(date)
    return JsonResponse({'slots': slots})


# ========== New Views for Medical History and Records ==========

@login_required(login_url='login')
def patient_medical_history(request):
    """Comprehensive patient medical history"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    # Get all medical information
    all_appointments = patient.appointments.all().select_related('doctor').order_by('-appointment_date')
    all_treatments = Treatment.objects.filter(appointment__patient=patient).select_related('appointment').order_by('-created_at')
    all_test_reports = patient.test_reports.all().order_by('-test_date')
    all_pathology_reports = patient.pathology_reports.all().order_by('-report_date')
    all_medical_records = patient.medical_records.all().order_by('-date_created')
    all_prescriptions = Prescription.objects.filter(patient=patient).order_by('-prescribed_date')
    
    context = {
        'patient': patient,
        'appointments': all_appointments,
        'treatments': all_treatments,
        'test_reports': all_test_reports,
        'pathology_reports': all_pathology_reports,
        'medical_records': all_medical_records,
        'prescriptions': all_prescriptions,
    }
    
    return render(request, 'clinic/patient_medical_history.html', context)


@login_required(login_url='login')
def patient_test_reports(request):
    """Patient test reports list"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    test_reports = patient.test_reports.all().order_by('-test_date')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        test_reports = test_reports.filter(status=status)
    
    context = {
        'test_reports': test_reports,
        'statuses': TestReport._meta.get_field('status').choices,
    }
    
    return render(request, 'clinic/patient_test_reports.html', context)


@login_required(login_url='login')
def patient_pathology_reports(request):
    """Patient pathology reports list"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    pathology_reports = patient.pathology_reports.all().order_by('-report_date')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        pathology_reports = pathology_reports.filter(status=status)
    
    context = {
        'pathology_reports': pathology_reports,
        'statuses': PathologyReport._meta.get_field('status').choices,
    }
    
    return render(request, 'clinic/patient_pathology_reports.html', context)


@login_required(login_url='login')
def patient_prescriptions(request):
    """Patient prescriptions list"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-prescribed_date')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        prescriptions = prescriptions.filter(status=status)
    
    context = {
        'prescriptions': prescriptions,
        'statuses': Prescription._meta.get_field('status').choices,
    }
    
    return render(request, 'clinic/patient_prescriptions.html', context)


@login_required(login_url='login')
def test_report_detail(request, report_id):
    """Test report detail view"""
    test_report = get_object_or_404(TestReport, id=report_id)
    
    # Check permission
    try:
        patient = request.user.patient
        if test_report.patient != patient:
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('home')
    except:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('home')
    
    context = {'test_report': test_report}
    return render(request, 'clinic/test_report_detail.html', context)


@login_required(login_url='login')
def pathology_report_detail(request, report_id):
    """Pathology report detail view"""
    pathology_report = get_object_or_404(PathologyReport, id=report_id)
    
    # Check permission
    try:
        patient = request.user.patient
        if pathology_report.patient != patient:
            messages.error(request, 'You do not have permission to view this report.')
            return redirect('home')
    except:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('home')
    
    context = {'pathology_report': pathology_report}
    return render(request, 'clinic/pathology_report_detail.html', context)


@login_required(login_url='login')
def update_doctor_profile(request):
    """Doctor profile update view"""
    try:
        doctor = request.user.doctor
    except:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = DoctorProfileUpdateForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = DoctorProfileUpdateForm(instance=doctor)
    
    context = {'form': form, 'profile_type': 'doctor'}
    return render(request, 'clinic/update_doctor_profile.html', context)


@login_required(login_url='login')
def update_patient_profile(request):
    """Patient profile update view"""
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = PatientProfileUpdateForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = PatientProfileUpdateForm(instance=patient)
    
    context = {'form': form, 'profile_type': 'patient'}
    return render(request, 'clinic/update_patient_profile.html', context)


# ========== Admin Dashboard Lite ==========

@login_required(login_url='login')
def admin_dashboard(request):
    """Custom admin dashboard (admin lite)"""
    # Check if user is admin/superuser
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    from django.db.models import Sum, Count, Q

    today = datetime.now().date()

    # Get statistics
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.filter(is_active=True).count()
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    active_doctors = Doctor.objects.filter(is_active=True).count()

    # Appointment statistics
    pending_appointments = Appointment.objects.filter(status='pending').count()
    confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancelled_appointments = Appointment.objects.filter(status='cancelled').count()

    # Treatment statistics
    total_treatments = Treatment.objects.count()
    completed_treatments = Treatment.objects.filter(status='completed').count()
    pending_treatments = Treatment.objects.filter(status__in=['recommended', 'in_progress']).count()

    # Revenue statistics
    total_revenue = Treatment.objects.aggregate(Sum('cost'))['cost__sum'] or 0
    paid_amount = Treatment.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    pending_revenue = total_revenue - paid_amount

    # Test and Pathology reports
    total_test_reports = TestReport.objects.count()
    pending_test_reports = TestReport.objects.filter(status='pending').count()
    completed_test_reports = TestReport.objects.filter(status='completed').count()

    total_pathology = PathologyReport.objects.count()
    pending_pathology = PathologyReport.objects.filter(status='pending').count()

    # Pharmacy statistics
    total_medicines = PharmacyInventory.objects.count()
    expired_medicines = PharmacyInventory.objects.filter(expiry_date__lt=datetime.now().date()).count()
    reorder_needed = PharmacyInventory.objects.filter(
        quantity__lte=models.F('reorder_level')
    ).count()

    # Get recent data
    recent_appointments = Appointment.objects.select_related(
        'patient', 'doctor'
    ).order_by('-created_at')[:8]

    recent_patients = Patient.objects.select_related('user').order_by('-created_at')[:5]

    recent_test_reports = TestReport.objects.select_related(
        'patient'
    ).order_by('-created_at')[:5]

    recent_pathology = PathologyReport.objects.select_related(
        'patient'
    ).order_by('-created_at')[:5]

    # Top doctors
    top_doctors = Doctor.objects.annotate(
        appointment_count=Count('appointments')
    ).order_by('-appointment_count')[:5]

    top_patients = []
    for patient in Patient.objects.select_related('user').annotate(
        visit_count=Count('appointments')
    ).order_by('-visit_count')[:4]:
        total_spend = patient.appointments.filter(treatment__isnull=False).aggregate(
            total=Sum('treatment__cost')
        )['total'] or 0
        next_appointment = patient.appointments.filter(
            appointment_date__gte=today
        ).order_by('appointment_date', 'appointment_time').first()
        patient.total_spend = total_spend
        patient.visit_count = patient.appointments.count()
        patient.next_appointment = next_appointment
        top_patients.append(patient)

    # Expired medicines alert
    expired_medicines_list = PharmacyInventory.objects.filter(
        expiry_date__lt=datetime.now().date()
    ).order_by('-expiry_date')[:5]

    # Medicines needing reorder
    reorder_medicines = PharmacyInventory.objects.filter(
        quantity__lte=models.F('reorder_level')
    ).order_by('quantity')[:5]

    context = {
        # Statistics
        'today': datetime.now(),
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'active_doctors': active_doctors,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,

        # Treatments
        'total_treatments': total_treatments,
        'completed_treatments': completed_treatments,
        'pending_treatments': pending_treatments,

        # Revenue
        'total_revenue': total_revenue,
        'paid_amount': paid_amount,
        'pending_revenue': pending_revenue,

        # Test reports
        'total_test_reports': total_test_reports,
        'pending_test_reports': pending_test_reports,
        'completed_test_reports': completed_test_reports,

        # Pathology
        'total_pathology': total_pathology,
        'pending_pathology': pending_pathology,

        # Pharmacy
        'total_medicines': total_medicines,
        'expired_medicines': expired_medicines,
        'reorder_needed': reorder_needed,

        # Recent data
        'recent_appointments': recent_appointments,
        'recent_patients': recent_patients,
        'recent_test_reports': recent_test_reports,
        'recent_pathology': recent_pathology,
        'top_doctors': top_doctors,
        'top_patients': top_patients,

        # Alerts
        'expired_medicines_list': expired_medicines_list,
        'reorder_medicines': reorder_medicines,
    }

    return render(request, 'clinic/admin_dashboard.html', context)


# ========== Patent Registration System ==========

@login_required(login_url='login')
def patent_list(request):
    """List all patent inventions"""
    if request.user.is_staff or request.user.is_superuser:
        patents = PatentInvention.objects.all().order_by('-created_at')
    else:
        patents = PatentInvention.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        patents = patents.filter(status=status)
    
    context = {
        'patents': patents,
        'statuses': PatentInvention._meta.get_field('status').choices,
        'current_status': status,
    }
    
    return render(request, 'clinic/patent_list.html', context)


@login_required(login_url='login')
def patent_create(request):
    """Create a new patent invention disclosure"""
    if request.method == 'POST':
        form = PatentInventionForm(request.POST, request.FILES)
        if form.is_valid():
            patent = form.save(commit=False)
            patent.user = request.user
            patent.save()
            messages.success(request, 'Patent invention disclosure submitted successfully!')
            return redirect('patent_detail', patent_id=patent.id)
    else:
        form = PatentInventionForm()
    
    context = {'form': form, 'title': 'Register Patent Invention'}
    return render(request, 'clinic/patent_form.html', context)


@login_required(login_url='login')
def patent_detail(request, patent_id):
    """View patent invention details"""
    patent = get_object_or_404(PatentInvention, id=patent_id)
    
    # Check permission
    if not (request.user.is_staff or request.user.is_superuser or patent.user == request.user):
        messages.error(request, 'You do not have permission to view this patent.')
        return redirect('patent_list')
    
    context = {'patent': patent}
    return render(request, 'clinic/patent_detail.html', context)


@login_required(login_url='login')
def patent_update(request, patent_id):
    """Update patent invention details"""
    patent = get_object_or_404(PatentInvention, id=patent_id)
    
    # Check permission - only owner or admin can update
    if not (request.user.is_staff or request.user.is_superuser or patent.user == request.user):
        messages.error(request, 'You do not have permission to update this patent.')
        return redirect('patent_detail', patent_id=patent.id)
    
    if request.method == 'POST':
        form = PatentInventionForm(request.POST, request.FILES, instance=patent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patent invention updated successfully!')
            return redirect('patent_detail', patent_id=patent.id)
    else:
        form = PatentInventionForm(instance=patent)
    
    context = {'form': form, 'patent': patent, 'title': 'Update Patent Invention'}
    return render(request, 'clinic/patent_form.html', context)


@login_required(login_url='login')
def patent_delete(request, patent_id):
    """Delete a patent invention"""
    patent = get_object_or_404(PatentInvention, id=patent_id)
    
    # Check permission - only owner or admin can delete
    if not (request.user.is_staff or request.user.is_superuser or patent.user == request.user):
        messages.error(request, 'You do not have permission to delete this patent.')
        return redirect('patent_detail', patent_id=patent.id)
    
    if request.method == 'POST':
        patent.delete()
        messages.success(request, 'Patent invention deleted successfully!')
        return redirect('patent_list')
    
    context = {'patent': patent}
    return render(request, 'clinic/patent_confirm_delete.html', context)

    
    recent_pathology = PathologyReport.objects.select_related(
        'patient'
    ).order_by('-created_at')[:5]
    
    # Top doctors
    top_doctors = Doctor.objects.annotate(
        appointment_count=Count('appointments')
    ).order_by('-appointment_count')[:5]
    
    # Expired medicines alert
    expired_medicines_list = PharmacyInventory.objects.filter(
        expiry_date__lt=datetime.now().date()
    ).order_by('-expiry_date')[:5]
    
    # Medicines needing reorder
    reorder_medicines = PharmacyInventory.objects.filter(
        quantity__lte=models.F('reorder_level')
    ).order_by('quantity')[:5]
    
    context = {
        # Statistics
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        
        # Treatments
        'total_treatments': total_treatments,
        'completed_treatments': completed_treatments,
        'pending_treatments': pending_treatments,
        
        # Revenue
        'total_revenue': total_revenue,
        'paid_amount': paid_amount,
        'pending_revenue': pending_revenue,
        
        # Reports
        'total_test_reports': total_test_reports,
        'pending_test_reports': pending_test_reports,
        'completed_test_reports': completed_test_reports,
        'total_pathology': total_pathology,
        'pending_pathology': pending_pathology,
        
        # Pharmacy
        'total_medicines': total_medicines,
        'expired_medicines': expired_medicines,
        'reorder_needed': reorder_needed,
        
        # Recent data
        'recent_appointments': recent_appointments,
        'recent_patients': recent_patients,
        'recent_test_reports': recent_test_reports,
        'recent_pathology': recent_pathology,
        'top_doctors': top_doctors,
        
        # Alerts
        'expired_medicines_list': expired_medicines_list,
        'reorder_medicines': reorder_medicines,
    }
    
    return render(request, 'clinic/admin_dashboard.html', context)


@login_required(login_url='login')
def doctor_desktop_console(request):
    """XE Dental Diamond Desktop Console Simulator"""
    try:
        doctor = request.user.doctor
    except:
        messages.error(request, 'Access denied: Only clinical staff can open the desktop console.')
        return redirect('home')
        
    # Handle POST patient registration from the retro console
    if request.method == 'POST' and request.POST.get('action') == 'register_patient':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        dob_str = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        emergency_contact = request.POST.get('emergency_contact')
        emergency_contact_phone = request.POST.get('emergency_contact_phone')
        blood_group = request.POST.get('blood_group', '')
        allergies = request.POST.get('allergies', '')
        medical_conditions = request.POST.get('medical_conditions', '')
        
        # Generate standard username and password
        username = f"{first_name.lower()}_{last_name.lower()}"
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        password = f"{first_name}123"  # Simple default password e.g. Vidhu123
        
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email or f"{username}@example.com"
            )
            Patient.objects.create(
                user=user,
                phone=phone,
                date_of_birth=datetime.strptime(dob_str, '%Y-%m-%d').date(),
                gender=gender,
                address=address or 'N/A',
                city=city or 'N/A',
                postal_code=postal_code or 'N/A',
                emergency_contact=emergency_contact or 'N/A',
                emergency_contact_phone=emergency_contact_phone or 'N/A',
                blood_group=blood_group,
                allergies=allergies,
                medical_conditions=medical_conditions
            )
            UserRole.objects.create(user=user, role='patient')
            messages.success(request, f"Patient successfully registered! Login: {username} / Pass: {password}")
        except Exception as e:
            messages.error(request, f"Failed to register patient: {str(e)}")
        return redirect('doctor_desktop_console')

    clinic = Clinic.objects.first()
    patients = Patient.objects.all().select_related('user').order_by('user__first_name')
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user').order_by('-appointment_date', '-appointment_time')
    materials = PharmacyInventory.objects.all().order_by('medicine_name')
    treatments = Treatment.objects.filter(appointment__doctor=doctor).select_related('appointment__patient__user')
    
    # Financial metrics
    from django.db.models import Sum
    total_rev = treatments.aggregate(Sum('cost'))['cost__sum'] or 0
    paid = treatments.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    outstanding = total_rev - paid
    
    # Handle date filters for reminder widget
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    filtered_appointments = appointments
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            filtered_appointments = appointments.filter(appointment_date__range=[start_date, end_date])
        except ValueError:
            pass
            
    context = {
        'doctor': doctor,
        'clinic': clinic,
        'patients': patients,
        'appointments': appointments,
        'materials': materials,
        'treatments': treatments,
        'total_revenue': total_rev,
        'paid_amount': paid,
        'outstanding_amount': outstanding,
        'filtered_appointments': filtered_appointments,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'adult_upper': [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28],
        'adult_lower': [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38],
        'pediatric_upper': [55, 54, 53, 52, 51, 61, 62, 63, 64, 65],
        'pediatric_lower': [85, 84, 83, 82, 81, 71, 72, 73, 74, 75],
    }
    
    return render(request, 'clinic/doctor_desktop_console.html', context)

