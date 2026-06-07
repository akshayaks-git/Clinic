"""
Quick Start Script - Run this after installation to populate sample data
Usage: python manage.py shell < populate_data.py
"""

from clinic.models import Doctor, Patient, Clinic, UserRole, Appointment, Treatment, Medication
from django.contrib.auth.models import User
from datetime import datetime, timedelta

def create_sample_data():
    print("Creating sample data...")
    
    # Create clinic info
    clinic, created = Clinic.objects.get_or_create(
        name="Dr. Annops Dental Clinic",
        defaults={
            "address": "123 Dental Street, Medical City, MC 12345",
            "phone": "+1-800-DENTAL-1",
            "email": "info@annopsdental.com",
            "website": "https://www.annopsdental.com",
            "about": "Expert dental care with compassionate service. We provide comprehensive dental solutions with modern techniques and a caring approach to every patient."
        }
    )
    if created:
        print(f"✓ Clinic created: {clinic.name}")
    
    # Create sample doctors
    doctors_data = [
        {
            "username": "dr_smith",
            "email": "dr.smith@clinic.com",
            "first_name": "John",
            "last_name": "Smith",
            "specialization": "general",
            "license": "DEN-GEN-001",
            "experience": 15,
            "phone": "+1-555-0001",
            "bio": "Dr. Smith is a highly experienced general dentist with 15 years of practice.",
            "fee": 100.00
        },
        {
            "username": "dr_jones",
            "email": "dr.jones@clinic.com",
            "first_name": "Sarah",
            "last_name": "Jones",
            "specialization": "orthodontics",
            "license": "DEN-ORT-002",
            "experience": 12,
            "phone": "+1-555-0002",
            "bio": "Dr. Jones specializes in orthodontics and smile alignment.",
            "fee": 150.00
        },
        {
            "username": "dr_williams",
            "email": "dr.williams@clinic.com",
            "first_name": "Michael",
            "last_name": "Williams",
            "specialization": "cosmetic",
            "license": "DEN-COS-003",
            "experience": 10,
            "phone": "+1-555-0003",
            "bio": "Dr. Williams is an expert in cosmetic dentistry and smile makeovers.",
            "fee": 200.00
        },
    ]
    
    for doc_data in doctors_data:
        user, created = User.objects.get_or_create(
            username=doc_data["username"],
            defaults={
                "email": doc_data["email"],
                "first_name": doc_data["first_name"],
                "last_name": doc_data["last_name"]
            }
        )
        if created:
            user.set_password("DoctorPass123!")
            user.save()
        
        doctor, created = Doctor.objects.get_or_create(
            user=user,
            defaults={
                "specialization": doc_data["specialization"],
                "license_number": doc_data["license"],
                "experience_years": doc_data["experience"],
                "phone": doc_data["phone"],
                "bio": doc_data["bio"],
                "consultation_fee": doc_data["fee"]
            }
        )
        if created:
            print(f"✓ Doctor created: Dr. {doc_data['first_name']} {doc_data['last_name']}")
        
        UserRole.objects.get_or_create(user=user, defaults={"role": "doctor"})
    
    # Create sample patients
    patients_data = [
        {
            "username": "john_doe",
            "email": "john@email.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1-555-1234",
            "dob": "1990-05-15",
            "gender": "M",
            "address": "456 Patient Ave, City",
            "city": "City",
            "postal": "12345",
            "emergency": "Jane Doe",
            "emergency_phone": "+1-555-5678",
            "blood": "O+"
        },
        {
            "username": "jane_smith",
            "email": "jane@email.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "+1-555-5678",
            "dob": "1992-08-22",
            "gender": "F",
            "address": "789 Oak Street, City",
            "city": "City",
            "postal": "12346",
            "emergency": "John Smith",
            "emergency_phone": "+1-555-1234",
            "blood": "A+"
        },
    ]
    
    for patient_data in patients_data:
        user, created = User.objects.get_or_create(
            username=patient_data["username"],
            defaults={
                "email": patient_data["email"],
                "first_name": patient_data["first_name"],
                "last_name": patient_data["last_name"]
            }
        )
        if created:
            user.set_password("PatientPass123!")
            user.save()
        
        from datetime import datetime
        dob = datetime.strptime(patient_data["dob"], "%Y-%m-%d").date()
        
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={
                "phone": patient_data["phone"],
                "date_of_birth": dob,
                "gender": patient_data["gender"],
                "address": patient_data["address"],
                "city": patient_data["city"],
                "postal_code": patient_data["postal"],
                "emergency_contact": patient_data["emergency"],
                "emergency_contact_phone": patient_data["emergency_phone"],
                "blood_group": patient_data["blood"]
            }
        )
        if created:
            print(f"✓ Patient created: {patient_data['first_name']} {patient_data['last_name']}")
        
        UserRole.objects.get_or_create(user=user, defaults={"role": "patient"})
    
    print("\n✓ Sample data populated successfully!")
    print("\nLogin Credentials:")
    print("Doctor: dr_smith / DoctorPass123!")
    print("Patient: john_doe / PatientPass123!")

if __name__ == "__main__":
    create_sample_data()
