import os
import django
from datetime import datetime, timedelta
import random
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dental_clinic.settings')
django.setup()

from django.contrib.auth.models import User
from clinic.models import (
    Doctor, Patient, Clinic, UserRole, Appointment, 
    Treatment, Medication, TestReport, PathologyReport, 
    PharmacyInventory, Prescription
)

def populate_database():
    print("--- Cleaning existing data ---")
    # Clean up existing data to prevent conflicts
    Appointment.objects.all().delete()
    Treatment.objects.all().delete()
    Medication.objects.all().delete()
    TestReport.objects.all().delete()
    PathologyReport.objects.all().delete()
    Prescription.objects.all().delete()
    Doctor.objects.all().delete()
    Patient.objects.all().delete()
    UserRole.objects.all().delete()
    Clinic.objects.all().delete()
    
    # Delete non-superuser accounts
    User.objects.filter(is_superuser=False).delete()

    print("--- Creating Clinic Information ---")
    clinic = Clinic.objects.create(
        name="Dr. Anoop's Anupam Dental Clinic",
        address="Nannambra, Theyyala, Malappuram, Kerala, India - 676320",
        phone="+91 9446046868",
        email="anoopkranupam@gmail.com",
        website="https://dranoopsdentalclinic.com",
        opening_time="09:00:00",
        closing_time="18:30:00",
        about=(
            "Dr. Anoop's Anupam Dental Clinic, led by Dr. Anoopkumar R, has been caring for patients since "
            "19th August 1996. For nearly three decades, we have remained committed to ethical dentistry, "
            "clear communication, and compassionate care. Word-of-mouth recommendations from generations "
            "of happy families shape our growth, reflecting our strict protocols for safety, sterilization, "
            "and child-friendly dental care."
        )
    )
    print(f"Clinic created: {clinic.name}")

    print("--- Creating Official Doctors ---")
    
    # Primary Doctor requested by user
    chief_doctor_info = {
        "username": "Anoop",
        "email": "dr.anoop@dranoopsdentalclinic.com",
        "password": "Anoop123",
        "first_name": "Anoopkumar",
        "last_name": "R",
        "specialization": "general",
        "license": "DEN-1732",
        "experience": 30,
        "phone": "+91 9446046868",
        "bio": "Dr. Anoopkumar R, BDS, is the Founder and Chief Dental Surgeon at Anupam Dental Clinic. With nearly three decades of clinical expertise, he is dedicated to delivering high-quality general and preventive dental care. He founded the clinic on August 19, 1996, with a core philosophy of trust, ethical dentistry, and clear communication.",
        "fee": 300.00
    }
    
    # Other specialist doctors (given random passwords and distinct profile usernames so they cannot be logged in with default credentials)
    other_doctors_info = [
        {
            "username": "profile_terry",
            "email": "dr.terry@dranoopsdentalclinic.com",
            "first_name": "Terry Thomas",
            "last_name": "Edathotty",
            "specialization": "orthodontics",
            "license": "DEN-4807",
            "experience": 18,
            "phone": "+91 9845012345",
            "bio": "Dr. Terry Thomas Edathotty, MDS, is a Senior Orthodontist specializing in aligners, braces, and cosmetic smile alignments. He offers advanced orthodontic care for children, adolescents, and adults, integrating digital treatment design with aesthetic orthodontic solutions.",
            "fee": 500.00
        },
        {
            "username": "profile_krishnakumar",
            "email": "dr.krishna@dranoopsdentalclinic.com",
            "first_name": "KrishnaKumar",
            "last_name": "R",
            "specialization": "pedodontics",
            "license": "DEN-7729",
            "experience": 12,
            "phone": "+91 9567012345",
            "bio": "Dr. KrishnaKumar, MDS, is a dedicated Pediatric Dentist (Paedodontist) focusing on interceptive and myofunctional treatments for children. He is known for creating a friendly, comforting, and welcoming clinical environment that keeps young patients relaxed.",
            "fee": 400.00
        },
        {
            "username": "profile_renjith",
            "email": "dr.renjith@dranoopsdentalclinic.com",
            "first_name": "Renjith",
            "last_name": "Raj",
            "specialization": "endodontics",
            "license": "DEN-8171",
            "experience": 10,
            "phone": "+91 9495012345",
            "bio": "Dr. Renjith Raj, MDS, is a skilled Endodontist specializing in advanced root canal treatments and microscopic endodontics. He is dedicated to single-sitting root canals and pain-free restorative procedures.",
            "fee": 450.00
        },
        {
            "username": "profile_justin",
            "email": "dr.justin@dranoopsdentalclinic.com",
            "first_name": "Justin",
            "last_name": "Mathew",
            "specialization": "oral_surgery",
            "license": "DEN-5492",
            "experience": 15,
            "phone": "+91 9895012345",
            "bio": "Dr. Justin Mathew, MDS, is an Oral & Maxillofacial Surgeon specializing in wisdom teeth extractions, implantology, trauma, and advanced laser-assisted dental surgeries. He focuses on minimally invasive procedures and rapid post-op recovery.",
            "fee": 550.00
        },
        {
            "username": "profile_joseph",
            "email": "dr.joseph@dranoopsdentalclinic.com",
            "first_name": "Joseph J",
            "last_name": "Pulikkottil",
            "specialization": "periodontics",
            "license": "DEN-2418",
            "experience": 22,
            "phone": "+91 9447012345",
            "bio": "Dr. Joseph J. Pulikkottil, MDS, is a Senior Periodontist and Implantologist. He specializes in advanced laser treatments for gums, pocket therapy, bone grafting, and dental implants. He brings precision and biological planning to restorative implants.",
            "fee": 600.00
        },
        {
            "username": "profile_sijo",
            "email": "dr.sijo@dranoopsdentalclinic.com",
            "first_name": "Sijo P",
            "last_name": "Mathew",
            "specialization": "endodontics",
            "license": "DEN-8982",
            "experience": 11,
            "phone": "+91 9747012345",
            "bio": "Dr. Sijo P. Mathew, MDS, is a Conservative Dentist and Endodontist. He brings clinical rigor to complex retreatment of root canals, cosmetic teeth filings, and complex tooth restorations.",
            "fee": 450.00
        },
        {
            "username": "profile_shibu",
            "email": "dr.shibu@dranoopsdentalclinic.com",
            "first_name": "Shibu",
            "last_name": "Sreedhar",
            "specialization": "endodontics",
            "license": "DEN-1561-A",
            "experience": 20,
            "phone": "+91 9847012345",
            "bio": "Dr. Shibu Sreedhar, MDS, is a Senior Endodontist and Smile Designer. With 20 years of practice, he integrates restorative endodontics with dental cosmetics like veneers, laminates, and computerized smile designs.",
            "fee": 500.00
        }
    ]

    doctor_instances = []
    
    # Create the 'Anoop' user
    chief_user = User.objects.create_user(
        username=chief_doctor_info["username"],
        email=chief_doctor_info["email"],
        password=chief_doctor_info["password"],
        first_name=chief_doctor_info["first_name"],
        last_name=chief_doctor_info["last_name"]
    )
    chief_doctor = Doctor.objects.create(
        user=chief_user,
        specialization=chief_doctor_info["specialization"],
        license_number=chief_doctor_info["license"],
        experience_years=chief_doctor_info["experience"],
        phone=chief_doctor_info["phone"],
        bio=chief_doctor_info["bio"],
        consultation_fee=chief_doctor_info["fee"],
        working_days="monday,tuesday,wednesday,thursday,friday,saturday"
    )
    UserRole.objects.create(user=chief_user, role="doctor")
    doctor_instances.append(chief_doctor)
    print(f"  Doctor (Anoop): Dr. {chief_user.first_name} {chief_user.last_name}")

    # Create the other doctors
    for doc in other_doctors_info:
        user = User.objects.create_user(
            username=doc["username"],
            email=doc["email"],
            password=str(uuid.uuid4()), # Unpredictable password for non-login placeholder accounts
            first_name=doc["first_name"],
            last_name=doc["last_name"]
        )
        doctor = Doctor.objects.create(
            user=user,
            specialization=doc["specialization"],
            license_number=doc["license"],
            experience_years=doc["experience"],
            phone=doc["phone"],
            bio=doc["bio"],
            consultation_fee=doc["fee"],
            working_days="monday,tuesday,wednesday,thursday,friday,saturday"
        )
        UserRole.objects.create(user=user, role="doctor")
        doctor_instances.append(doctor)
        print(f"  Doctor: Dr. {user.first_name} {user.last_name}")

    print("--- Creating Patient Account ---")
    patient_user = User.objects.create_user(
        username="vidhu",
        email="vidhu@example.com",
        password="Vidhu123",
        first_name="Vidhu",
        last_name="Patient"
    )
    patient = Patient.objects.create(
        user=patient_user,
        phone="+91 9900112233",
        date_of_birth=datetime.strptime("1994-07-20", "%Y-%m-%d").date(),
        gender="F",
        address="Near Theyyala Junction",
        city="Malappuram",
        postal_code="676320",
        emergency_contact="Family Member",
        emergency_contact_phone="+91 9446123456",
        blood_group="B+",
        medical_conditions="Penicillin allergy"
    )
    UserRole.objects.create(user=patient_user, role="patient")
    print(f"  Patient (vidhu): {patient_user.first_name} {patient_user.last_name}")

    print("--- Creating Sample Appointments & Treatments for vidhu ---")
    reasons = [
        "Regular dental cleaning and checkup",
        "Severe toothache in lower left molar",
        "Orthodontic consultation for clear aligners",
        "Gingival bleeding during brushing",
        "Consultation for tooth implant"
    ]
    
    treatment_types = [
        ("Scaling", "Teeth cleaning and plaque removal", 1200.00),
        ("Root Canal Treatment", "Painless RCT followed by dental crown", 4500.00),
        ("Aligners Checkup", "Monthly checkup for clear aligner set", 2500.00),
        ("Composite Filling", "Tooth-colored composite restoration", 1500.00),
        ("Dental Implant", "First stage dental implant placement", 35000.00)
    ]

    today = datetime.now().date()
    
    # Create past appointments and treatments for vidhu
    for i in range(5):
        doc = random.choice(doctor_instances)
        app_date = today - timedelta(days=random.randint(2, 60))
        app_time = f"{random.choice([9, 10, 11, 14, 15, 16])}:00:00"
        
        app = Appointment.objects.create(
            patient=patient,
            doctor=doc,
            appointment_date=app_date,
            appointment_time=app_time,
            reason=random.choice(reasons),
            status='completed',
            notes="Treatment successfully completed."
        )
        
        t_type, t_desc, t_cost = random.choice(treatment_types)
        paid = random.choice([t_cost, t_cost * 0.5])
        status = 'completed' if paid == t_cost else 'in_progress'
        
        Treatment.objects.create(
            appointment=app,
            treatment_type=t_type,
            description=t_desc,
            status=status,
            start_date=app_date,
            actual_end_date=app_date if status == 'completed' else None,
            cost=t_cost,
            paid_amount=paid,
            notes="Patient advised to maintain hygiene."
        )

    # Create upcoming appointments for vidhu
    for i in range(2):
        doc = random.choice(doctor_instances)
        app_date = today + timedelta(days=random.randint(1, 10))
        app_time = f"{random.choice([9, 10, 11, 14, 15, 16])}:00:00"
        
        Appointment.objects.create(
            patient=patient,
            doctor=doc,
            appointment_date=app_date,
            appointment_time=app_time,
            reason=random.choice(reasons),
            status='confirmed'
        )

    print("--- Creating Pharmacy Inventory ---")
    medicines = [
        {"name": "Amoxicillin 500mg", "gen": "Amoxicillin", "cat": "Antibiotic", "qty": 150, "cost": 3.00, "sell": 6.00, "exp": today + timedelta(days=365)},
        {"name": "Ibuprofen 400mg", "gen": "Ibuprofen", "cat": "Analgesic", "qty": 300, "cost": 1.50, "sell": 3.00, "exp": today + timedelta(days=200)},
        {"name": "Ketorolac 10mg", "gen": "Ketorolac", "cat": "Analgesic", "qty": 80, "cost": 2.50, "sell": 5.00, "exp": today + timedelta(days=400)},
        {"name": "Chlorhexidine Mouthwash 0.2%", "gen": "Chlorhexidine Gluconate", "cat": "Mouthwash", "qty": 12, "cost": 45.00, "sell": 90.00, "exp": today + timedelta(days=90)},
        {"name": "Paracetamol 650mg", "gen": "Paracetamol", "cat": "Analgesic", "qty": 500, "cost": 0.80, "sell": 2.00, "exp": today + timedelta(days=500)},
        {"name": "Clindamycin 300mg", "gen": "Clindamycin", "cat": "Antibiotic", "qty": 4, "cost": 8.00, "sell": 15.00, "exp": today + timedelta(days=600)},
        {"name": "Dental Glass Ionomer Cement", "gen": "GIC Filling Kit", "cat": "Dental cement", "qty": 2, "cost": 250.00, "sell": 450.00, "exp": today + timedelta(days=300)},
    ]

    for med in medicines:
        PharmacyInventory.objects.create(
            medicine_name=med["name"],
            generic_name=med["gen"],
            manufacturer="Astra Health / DentalCorp",
            batch_number=f"BCH-{random.randint(1000, 9999)}",
            unit="tablet" if "Mouthwash" not in med["name"] and "Cement" not in med["name"] else "bottle",
            quantity=med["qty"],
            cost_per_unit=med["cost"],
            selling_price=med["sell"],
            expiry_date=med["exp"],
            reorder_level=10,
            supplier="Standard Dental Distributors",
            notes="Store in a cool dry place."
        )
    print("Pharmacy stock populated successfully!")

    print("All real clinic information and doctors populated successfully!")

if __name__ == "__main__":
    populate_database()
