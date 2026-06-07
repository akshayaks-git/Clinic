from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/patient/', views.patient_register, name='patient_register'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
    
    # Admin Dashboard Lite
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # Profile
    path('profile/', views.my_profile, name='profile'),
    path('profile/update/doctor/', views.update_doctor_profile, name='update_doctor_profile'),
    path('profile/update/patient/', views.update_patient_profile, name='update_patient_profile'),
    
    # Doctors
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    
    # Appointments
    path('appointments/book/', views.book_appointment, name='book_appointment'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/<int:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    
    # Treatments
    path('patient/treatments/', views.patient_treatments, name='patient_treatments'),
    path('treatment/<int:treatment_id>/', views.treatment_detail, name='treatment_detail'),
    
    # Medical Records
    path('medical-records/', views.medical_records, name='medical_records'),
    path('medical-records/add/', views.add_medical_record, name='add_medical_record'),
    
    # Medical History & Reports
    path('patient/medical-history/', views.patient_medical_history, name='patient_medical_history'),
    path('patient/test-reports/', views.patient_test_reports, name='patient_test_reports'),
    path('patient/test-reports/<int:report_id>/', views.test_report_detail, name='test_report_detail'),
    path('patient/pathology-reports/', views.patient_pathology_reports, name='patient_pathology_reports'),
    path('patient/pathology-reports/<int:report_id>/', views.pathology_report_detail, name='pathology_report_detail'),
    path('patient/prescriptions/', views.patient_prescriptions, name='patient_prescriptions'),
    
    # Patent Registration System
    path('patents/', views.patent_list, name='patent_list'),
    path('patents/register/', views.patent_create, name='patent_create'),
    path('patents/<int:patent_id>/', views.patent_detail, name='patent_detail'),
    path('patents/<int:patent_id>/edit/', views.patent_update, name='patent_update'),
    path('patents/<int:patent_id>/delete/', views.patent_delete, name='patent_delete'),
    
    # API
    path('api/available-slots/<int:doctor_id>/', views.get_available_slots, name='get_available_slots'),
    
    # XE Dental Diamond Desktop Console
    path('doctor/desktop/', views.doctor_desktop_console, name='doctor_desktop_console'),
]
