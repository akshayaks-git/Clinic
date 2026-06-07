from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from .models import Doctor, Patient, Appointment, Treatment, Medication, MedicalRecord, Clinic, UserRole, TestReport, PathologyReport, PharmacyInventory, Prescription


class DashboardAdminSite(admin.AdminSite):
    site_header = "Dr. Annops Dental Clinic Admin"
    site_title = "Dental Clinic Admin"
    index_title = "Dashboard"
    index_template = 'admin/index.html'
    
    def index(self, request, extra_context=None):
        """Render custom dashboard index"""
        # Get statistics
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.filter(is_active=True).count()
        total_appointments = Appointment.objects.count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        pending_appointments = Appointment.objects.filter(status='pending').count()
        confirmed_appointments = Appointment.objects.filter(status='confirmed').count()
        cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
        
        # Revenue statistics
        total_revenue = Treatment.objects.aggregate(Sum('cost'))['cost__sum'] or 0
        paid_amount = Treatment.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        pending_revenue = total_revenue - paid_amount
        
        # Recent appointments
        recent_appointments = Appointment.objects.select_related(
            'patient', 'doctor'
        ).order_by('-created_at')[:5]
        
        # Recent treatments
        recent_treatments = Treatment.objects.select_related(
            'appointment__patient'
        ).order_by('-created_at')[:5]
        
        # Top doctors by appointments
        top_doctors = Doctor.objects.annotate(
            appointment_count=Count('appointments')
        ).order_by('-appointment_count')[:5]
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'pending_appointments': pending_appointments,
            'confirmed_appointments': confirmed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'total_revenue': total_revenue,
            'paid_amount': paid_amount,
            'pending_revenue': pending_revenue,
            'recent_appointments': recent_appointments,
            'recent_treatments': recent_treatments,
            'top_doctors': top_doctors,
        })
        
        return super().index(request, extra_context)


# Replace the default admin site
admin.site.__class__ = DashboardAdminSite
admin.site.site_header = "Dr. Annops Dental Clinic Admin"
admin.site.site_title = "Dental Clinic Admin"
admin.site.index_title = "Dashboard"
admin.site.index_template = 'admin/index.html'
admin.site.index = DashboardAdminSite.index.__get__(admin.site, type(admin.site))

# Now register models with the default admin site
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'opening_time', 'closing_time']
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'logo')}),
        ('Contact', {'fields': ('phone', 'email', 'website')}),
        ('Address', {'fields': ('address',)}),
        ('Hours', {'fields': ('opening_time', 'closing_time')}),
        ('About', {'fields': ('about',)}),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_doctor_name', 'specialization', 'license_number', 'experience_years', 'is_active', 'consultation_fee']
    list_filter = ['specialization', 'is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'license_number']
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Professional Details', {'fields': ('specialization', 'license_number', 'experience_years', 'bio')}),
        ('Contact', {'fields': ('phone',)}),
        ('Schedule', {'fields': ('working_days', 'start_time', 'end_time')}),
        ('Fees', {'fields': ('consultation_fee',)}),
        ('Profile', {'fields': ('profile_image', 'is_active')}),
    )
    actions = ['make_active', 'make_inactive']

    def get_doctor_name(self, obj):
        return f"Dr. {obj.user.first_name} {obj.user.last_name}"
    get_doctor_name.short_description = 'Name'

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} doctor(s) activated.')
    make_active.short_description = 'Activate selected doctors'

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} doctor(s) deactivated.')
    make_inactive.short_description = 'Deactivate selected doctors'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_patient_name', 'phone', 'city', 'age', 'created_at']
    list_filter = ['gender', 'city', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'phone']
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Personal Details', {'fields': ('date_of_birth', 'gender', 'profile_image')}),
        ('Contact', {'fields': ('phone', 'address', 'city', 'postal_code')}),
        ('Emergency Contact', {'fields': ('emergency_contact', 'emergency_contact_phone')}),
        ('Medical Information', {'fields': ('blood_group', 'allergies', 'medical_conditions')}),
    )

    def get_patient_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_patient_name.short_description = 'Name'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['get_appointment_info', 'appointment_date', 'appointment_time', 'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'doctor']
    search_fields = ['patient__user__first_name', 'doctor__user__first_name', 'reason']
    fieldsets = (
        ('Appointment Details', {'fields': ('patient', 'doctor', 'appointment_date', 'appointment_time', 'duration_minutes')}),
        ('Information', {'fields': ('reason', 'status', 'notes')}),
    )

    def get_appointment_info(self, obj):
        return f"{obj.patient.user.first_name} - Dr. {obj.doctor.user.first_name}"
    get_appointment_info.short_description = 'Appointment'


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['treatment_type', 'get_patient_name', 'status', 'cost', 'payment_status', 'updated_at']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['treatment_type', 'appointment__patient__user__first_name']
    fieldsets = (
        ('Treatment Information', {'fields': ('appointment', 'treatment_type', 'description')}),
        ('Status', {'fields': ('status', 'start_date', 'estimated_end_date', 'actual_end_date')}),
        ('Cost', {'fields': ('cost', 'paid_amount')}),
        ('Notes', {'fields': ('notes',)}),
    )

    def get_patient_name(self, obj):
        return obj.appointment.patient.user.first_name
    get_patient_name.short_description = 'Patient'


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'dosage', 'frequency', 'duration_days', 'get_patient_name']
    list_filter = ['frequency', 'prescribed_date']
    search_fields = ['medicine_name', 'treatment__appointment__patient__user__first_name']

    def get_patient_name(self, obj):
        return obj.treatment.appointment.patient.user.first_name
    get_patient_name.short_description = 'Patient'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['record_type', 'get_patient_name', 'date_created', 'file']
    list_filter = ['record_type', 'date_created']
    search_fields = ['patient__user__first_name', 'record_type']

    def get_patient_name(self, obj):
        return obj.patient.user.first_name
    get_patient_name.short_description = 'Patient'


@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'get_patient_name', 'test_type', 'test_date', 'status']
    list_filter = ['test_type', 'status', 'test_date']
    search_fields = ['test_name', 'patient__user__first_name', 'patient__user__last_name']
    fieldsets = (
        ('Patient Information', {'fields': ('patient', 'doctor')}),
        ('Test Details', {'fields': ('test_type', 'test_name', 'description')}),
        ('Report', {'fields': ('test_date', 'report_file', 'result_summary')}),
        ('Status', {'fields': ('status', 'notes')}),
    )

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
    get_patient_name.short_description = 'Patient'


@admin.register(PathologyReport)
class PathologyReportAdmin(admin.ModelAdmin):
    list_display = ['test_name', 'get_patient_name', 'report_date', 'status']
    list_filter = ['status', 'report_date']
    search_fields = ['test_name', 'patient__user__first_name', 'patient__user__last_name']
    fieldsets = (
        ('Patient Information', {'fields': ('patient', 'doctor')}),
        ('Report Details', {'fields': ('test_name', 'sample_date', 'report_date')}),
        ('Findings', {'fields': ('findings', 'recommendations')}),
        ('Report', {'fields': ('report_file',)}),
        ('Status', {'fields': ('status', 'notes')}),
    )

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
    get_patient_name.short_description = 'Patient'


@admin.register(PharmacyInventory)
class PharmacyInventoryAdmin(admin.ModelAdmin):
    list_display = ['medicine_name', 'batch_number', 'quantity', 'cost_per_unit', 'selling_price', 'display_is_expired', 'display_needs_reorder']
    list_filter = ['unit', 'expiry_date', 'created_at']
    search_fields = ['medicine_name', 'generic_name', 'batch_number']
    fieldsets = (
        ('Medicine Information', {'fields': ('medicine_name', 'generic_name', 'manufacturer')}),
        ('Inventory', {'fields': ('batch_number', 'quantity', 'unit', 'reorder_level')}),
        ('Pricing', {'fields': ('cost_per_unit', 'selling_price')}),
        ('Dates', {'fields': ('expiry_date',)}),
        ('Supplier', {'fields': ('supplier',)}),
        ('Notes', {'fields': ('notes',)}),
    )

    def display_is_expired(self, obj):
        return obj.is_expired
    display_is_expired.boolean = True
    display_is_expired.short_description = 'Expired'

    def display_needs_reorder(self, obj):
        return obj.needs_reorder
    display_needs_reorder.boolean = True
    display_needs_reorder.short_description = 'Needs Reorder'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['medicine', 'get_patient_name', 'dosage', 'frequency', 'status', 'prescribed_date']
    list_filter = ['status', 'frequency', 'prescribed_date']
    search_fields = ['medicine', 'patient__user__first_name', 'patient__user__last_name']
    fieldsets = (
        ('Patient Information', {'fields': ('patient', 'doctor', 'appointment')}),
        ('Prescription Details', {'fields': ('medicine', 'dosage', 'frequency', 'duration_days')}),
        ('Instructions', {'fields': ('instructions',)}),
        ('Status', {'fields': ('status',)}),
    )

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
    get_patient_name.short_description = 'Patient'
