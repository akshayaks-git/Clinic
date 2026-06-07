from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta

class Doctor(models.Model):
    SPECIALIZATION_CHOICES = [
        ('general', 'General Dentist'),
        ('orthodontics', 'Orthodontist'),
        ('periodontics', 'Periodontist'),
        ('endodontics', 'Endodontist'),
        ('prosthodontics', 'Prosthodontist'),
        ('pedodontics', 'Pediatric Dentist'),
        ('oral_surgery', 'Oral Surgeon'),
        ('cosmetic', 'Cosmetic Dentist'),
    ]

    DAYS_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.IntegerField(validators=[MinValueValidator(0)])
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='doctor_profiles/', null=True, blank=True)
    phone = models.CharField(max_length=20)
    working_days = models.CharField(max_length=100, default='monday,tuesday,wednesday,thursday,friday')
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='17:00')
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.get_specialization_display()}"

    def get_available_slots(self, date):
        """Get available appointment slots for a given date"""
        from datetime import time, datetime as dt, timedelta
        
        day_name = date.strftime('%A').lower()
        working_days = self.working_days.split(',')
        
        if day_name not in working_days:
            return []
        
        start = dt.combine(date, self.start_time)
        end = dt.combine(date, self.end_time)
        slots = []
        
        current = start
        while current < end:
            slots.append(current.strftime('%H:%M'))
            current += timedelta(minutes=30)
        
        # Remove booked slots
        booked_appointments = Appointment.objects.filter(
            doctor=self,
            appointment_date=date,
            status__in=['confirmed', 'completed']
        ).values_list('appointment_time', flat=True)
        
        available_slots = [slot for slot in slots if slot not in booked_appointments]
        return available_slots


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    emergency_contact = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    blood_group = models.CharField(max_length=10, blank=True)
    allergies = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='patient_profiles/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def age(self):
        today = datetime.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.IntegerField(default=30)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']

    def __str__(self):
        return f"Appointment - {self.patient.user.first_name} with {self.doctor.user.first_name} on {self.appointment_date}"

    @property
    def is_upcoming(self):
        from datetime import datetime as dt
        appointment_datetime = dt.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime > dt.now() and self.status == 'confirmed'

    @property
    def is_past(self):
        from datetime import datetime as dt
        appointment_datetime = dt.combine(self.appointment_date, self.appointment_time)
        return appointment_datetime < dt.now()


class Treatment(models.Model):
    STATUS_CHOICES = [
        ('recommended', 'Recommended'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]

    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='treatment')
    treatment_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recommended')
    start_date = models.DateField(null=True, blank=True)
    estimated_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.treatment_type} - {self.appointment.patient.user.first_name}"

    @property
    def pending_amount(self):
        return self.cost - self.paid_amount

    @property
    def payment_status(self):
        if self.paid_amount == 0:
            return 'Unpaid'
        elif self.paid_amount < self.cost:
            return 'Partial'
        else:
            return 'Paid'


class Medication(models.Model):
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('thrice_daily', 'Three Times Daily'),
        ('every_6_hours', 'Every 6 Hours'),
        ('every_8_hours', 'Every 8 Hours'),
        ('as_needed', 'As Needed'),
    ]

    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='medications')
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_days = models.IntegerField()
    instructions = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    prescribed_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    record_type = models.CharField(max_length=50)  # X-ray, CT Scan, etc.
    description = models.TextField()
    file = models.FileField(upload_to='medical_records/')
    date_created = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.record_type} - {self.patient.user.first_name}"


class Clinic(models.Model):
    name = models.CharField(max_length=100, default='Dr. Annops Dental Clinic')
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    opening_time = models.TimeField(default='09:00')
    closing_time = models.TimeField(default='18:00')
    about = models.TextField()
    logo = models.ImageField(upload_to='clinic/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('receptionist', 'Receptionist'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class TestReport(models.Model):
    TEST_TYPE_CHOICES = [
        ('blood_test', 'Blood Test'),
        ('xray', 'X-Ray'),
        ('ct_scan', 'CT Scan'),
        ('ultrasound', 'Ultrasound'),
        ('pathology', 'Pathology'),
        ('mri', 'MRI'),
        ('ecg', 'ECG'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='test_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_reports')
    test_type = models.CharField(max_length=30, choices=TEST_TYPE_CHOICES)
    test_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test_date = models.DateField()
    report_file = models.FileField(upload_to='test_reports/')
    result_summary = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-test_date']

    def __str__(self):
        return f"{self.test_name} - {self.patient.user.first_name} ({self.test_date})"


class PathologyReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='pathology_reports')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='pathology_reports')
    test_name = models.CharField(max_length=200)
    sample_date = models.DateField()
    report_date = models.DateField()
    findings = models.TextField()
    recommendations = models.TextField(blank=True)
    report_file = models.FileField(upload_to='pathology_reports/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.test_name} - {self.patient.user.first_name} ({self.report_date})"


class PharmacyInventory(models.Model):
    UNIT_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('ml', 'ML'),
        ('vial', 'Vial'),
        ('strip', 'Strip'),
        ('bottle', 'Bottle'),
    ]

    medicine_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    batch_number = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateField()
    reorder_level = models.IntegerField(default=10)
    supplier = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['medicine_name']

    def __str__(self):
        return f"{self.medicine_name} ({self.batch_number})"

    @property
    def is_expired(self):
        return datetime.now().date() > self.expiry_date

    @property
    def needs_reorder(self):
        return self.quantity <= self.reorder_level


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    medicine = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    instructions = models.TextField(blank=True)
    prescribed_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prescribed_date']

    def __str__(self):
        return f"{self.medicine} - {self.patient.user.first_name}"


class PatentInvention(models.Model):
    INNOVATION_TYPE_CHOICES = [
        ('dental_instrument', 'Dental Instrument'),
        ('dental_equipment', 'Dental Equipment'),
        ('dental_software', 'Dental Software'),
        ('dental_material', 'Dental Material'),
        ('treatment_method', 'Treatment Method'),
        ('diagnostic_tool', 'Diagnostic Tool'),
        ('ai_solution', 'AI-Based Solution'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('filed', 'Filed with Patent Office'),
        ('granted', 'Patent Granted'),
    ]

    # Applicant Information
    applicant_name = models.CharField(max_length=200)
    clinic_name = models.CharField(max_length=200)
    clinic_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    email_address = models.EmailField()
    
    # Inventor Details
    inventor_names = models.TextField(help_text="Comma-separated list of inventor names")
    inventor_designations = models.TextField(blank=True, help_text="Comma-separated designations")
    inventor_contact = models.TextField(blank=True, help_text="Comma-separated contact numbers")
    
    # Invention Details
    title = models.CharField(max_length=300)
    innovation_type = models.CharField(max_length=30, choices=INNOVATION_TYPE_CHOICES)
    problem_statement = models.TextField(help_text="Describe the problem or limitation in current dental practice")
    detailed_description = models.TextField(help_text="Provide a complete explanation of the invention")
    novel_features = models.TextField(help_text="What makes the invention new and unique?")
    advantages = models.TextField(help_text="List the benefits compared to existing solutions")
    
    # Technical Documentation
    technical_drawings = models.FileField(upload_to='patent_drawings/', null=True, blank=True)
    technical_specifications = models.FileField(upload_to='patent_specs/', null=True, blank=True)
    
    # Prior Art & Disclosure
    prior_art_search_done = models.BooleanField(default=False)
    prior_art_details = models.TextField(blank=True)
    public_disclosure = models.BooleanField(default=False)
    public_disclosure_details = models.TextField(blank=True)
    
    # Commercial Information
    expected_applications = models.TextField(help_text="Expected applications and use cases")
    target_market = models.CharField(max_length=500)
    estimated_commercial_value = models.CharField(max_length=500, blank=True)
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    patentability_assessment = models.CharField(max_length=30, choices=[
        ('novel', 'Novel'),
        ('inventive_step', 'Inventive Step Present'),
        ('industrial_applicable', 'Industrially Applicable'),
        ('requires_review', 'Requires Further Review'),
    ], blank=True)
    
    # Reviewer Information
    reviewer_name = models.CharField(max_length=200, blank=True)
    review_date = models.DateField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # System Fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='patent_inventions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.applicant_name}"
