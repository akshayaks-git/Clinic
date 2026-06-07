from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Patient, Doctor, Appointment, Treatment, Medication, MedicalRecord, TestReport, PathologyReport, PharmacyInventory, Prescription, PatentInvention
from datetime import datetime, timedelta

class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=Patient._meta.get_field('gender').choices)
    address = forms.CharField(widget=forms.Textarea)
    city = forms.CharField(max_length=50)
    postal_code = forms.CharField(max_length=10)
    emergency_contact = forms.CharField(max_length=100)
    emergency_contact_phone = forms.CharField(max_length=20)
    blood_group = forms.CharField(max_length=10, required=False)
    allergies = forms.CharField(widget=forms.Textarea, required=False)
    medical_conditions = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class DoctorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20)
    specialization = forms.ChoiceField(choices=Doctor._meta.get_field('specialization').choices)
    license_number = forms.CharField(max_length=50)
    experience_years = forms.IntegerField(min_value=0)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    working_days = forms.CharField(max_length=100, initial='monday,tuesday,wednesday,thursday,friday')
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    consultation_fee = forms.DecimalField(decimal_places=2)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select a future date"
    )
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your dental issue or reason for visit'}),
        }

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date < datetime.now().date():
            raise forms.ValidationError("Cannot book appointment in the past.")
        if date > datetime.now().date() + timedelta(days=90):
            raise forms.ValidationError("Cannot book appointment more than 90 days in advance.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('appointment_date')
        time = cleaned_data.get('appointment_time')

        if doctor and date and time:
            # Check if slot is already booked
            existing = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=date,
                appointment_time=time,
                status__in=['confirmed', 'completed']
            ).exists()
            if existing:
                raise forms.ValidationError("This slot is already booked. Please choose another time.")

        return cleaned_data


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ['treatment_type', 'description', 'status', 'start_date', 'estimated_end_date', 'cost']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'estimated_end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['medicine_name', 'dosage', 'frequency', 'duration_days', 'instructions', 'side_effects']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 3}),
            'side_effects': forms.Textarea(attrs={'rows': 3}),
        }


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['record_type', 'description', 'file', 'notes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class TestReportForm(forms.ModelForm):
    class Meta:
        model = TestReport
        fields = ['test_type', 'test_name', 'description', 'test_date', 'report_file', 'result_summary', 'status', 'notes']
        widgets = {
            'test_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'result_summary': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class PathologyReportForm(forms.ModelForm):
    class Meta:
        model = PathologyReport
        fields = ['test_name', 'sample_date', 'report_date', 'findings', 'recommendations', 'report_file', 'status', 'notes']
        widgets = {
            'sample_date': forms.DateInput(attrs={'type': 'date'}),
            'report_date': forms.DateInput(attrs={'type': 'date'}),
            'findings': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class PharmacyInventoryForm(forms.ModelForm):
    class Meta:
        model = PharmacyInventory
        fields = ['medicine_name', 'generic_name', 'manufacturer', 'batch_number', 'unit', 'quantity', 
                  'cost_per_unit', 'selling_price', 'expiry_date', 'reorder_level', 'supplier', 'notes']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicine', 'dosage', 'frequency', 'duration_days', 'instructions', 'status']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 3}),
        }


class DoctorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialization', 'license_number', 'experience_years', 'bio', 'phone', 
                  'working_days', 'start_time', 'end_time', 'consultation_fee', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['phone', 'date_of_birth', 'gender', 'address', 'city', 'postal_code', 
                  'emergency_contact', 'emergency_contact_phone', 'blood_group', 'allergies', 
                  'medical_conditions', 'profile_image']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
        }


class PatentInventionForm(forms.ModelForm):
    class Meta:
        model = PatentInvention
        fields = [
            'applicant_name', 'clinic_name', 'clinic_address', 'phone_number', 'email_address',
            'inventor_names', 'inventor_designations', 'inventor_contact',
            'title', 'innovation_type', 'problem_statement', 'detailed_description',
            'novel_features', 'advantages', 'technical_drawings', 'technical_specifications',
            'prior_art_search_done', 'prior_art_details', 'public_disclosure', 'public_disclosure_details',
            'expected_applications', 'target_market', 'estimated_commercial_value'
        ]
        widgets = {
            'clinic_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter clinic address'}),
            'inventor_names': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter comma-separated inventor names'}),
            'inventor_designations': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter comma-separated designations'}),
            'inventor_contact': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter comma-separated contact numbers'}),
            'problem_statement': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the problem or limitation in current dental practice'}),
            'detailed_description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Provide a complete explanation of the invention'}),
            'novel_features': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What makes the invention new and unique?'}),
            'advantages': forms.Textarea(attrs={'rows': 4, 'placeholder': 'List the benefits compared to existing solutions'}),
            'prior_art_details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Provide details of similar patents found'}),
            'public_disclosure_details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Date, location, and event/publication details'}),
            'expected_applications': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Expected applications and use cases'}),
            'estimated_commercial_value': forms.TextInput(attrs={'placeholder': 'Estimated value (optional)'}),
        }

