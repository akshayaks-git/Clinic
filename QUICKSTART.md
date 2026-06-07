# Quick Start Guide - Dr. Annops Dental Clinic

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 4.2.13
- SQLite3 (included with Python)

### Installation Steps

1. **Install Dependencies**:
   ```bash
   cd dental_clinic
   pip install -r requirements.txt
   ```

2. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create Admin Account**:
   ```bash
   python manage.py createsuperuser
   # Follow prompts to create your admin account
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**:
   - Main Site: `http://localhost:8000/`
   - Admin Panel: `http://localhost:8000/admin/`

---

## 👥 User Roles

### 1. **Admin User**
- **Login**: `/login/`
- **Dashboard**: `/admin/`
- **Can**:
  - Manage all doctor profiles
  - Create and manage test reports
  - Create and manage pathology reports
  - Manage pharmacy inventory
  - Create prescriptions
  - View all patient records

### 2. **Doctor User**
- **Registration**: `/register/doctor/`
- **Dashboard**: `/doctor/dashboard/`
- **Can**:
  - Update their profile
  - View appointments
  - Confirm appointments
  - See patient information

### 3. **Patient User**
- **Registration**: `/register/patient/` (from home page)
- **Dashboard**: `/patient/dashboard/`
- **Can**:
  - Book appointments
  - View medical history
  - View test reports
  - View pathology reports
  - View prescriptions
  - Update their profile
  - View treatments and records

---

## 📋 Main Features

### For Patients
```
Dashboard Overview:
├── Statistics (Appointments, Treatments, Tests)
├── Quick Links (Medical History, Tests, Prescriptions, etc.)
├── Upcoming Appointments
├── Active Treatments
├── Recent Test Reports
├── Recent Prescriptions
├── Medical Records
└── Personal Information
```

### Medical History View
Complete medical information in one place:
- All appointments with dates and doctors
- All treatments with costs and status
- All test reports with downloadable files
- All pathology reports with findings
- All prescriptions with dosages
- All medical records

### Profile Management
- **Patient**: Update personal, address, emergency contact, medical history
- **Doctor**: Update specialization, experience, fees, working hours, bio

### Test & Report Management
- View test status (pending, in progress, completed, reviewed)
- Download report files
- See assigned doctor information
- View findings and recommendations

---

## 🏥 Admin Panel Features

### Test Report Management
Path: `/admin/clinic/testreport/`
- Add new test reports for patients
- Upload test files
- Track status
- Assign doctors
- Add result summaries

### Pathology Reports
Path: `/admin/clinic/pathologyreport/`
- Create pathology reports
- Add findings and recommendations
- Upload report files
- Track dates (sample date vs report date)

### Pharmacy Inventory
Path: `/admin/clinic/pharmacyinventory/`
- Add medicines to inventory
- Track batch numbers and quantities
- Set cost and selling prices
- Track expiry dates
- Automatic alerts for:
  - Expired medicines
  - Items needing reorder

### Doctor Management
Path: `/admin/clinic/doctor/`
- Create/edit doctor profiles
- Manage specialization and license
- Set working hours and fees
- Bulk activate/deactivate doctors
- Upload profile images

---

## 🔐 Login Credentials

### Create Test Accounts

#### Option 1: Using Admin Panel
1. Go to `/admin/`
2. Login with superuser
3. Click "Users" and create new users
4. Assign roles as patient/doctor

#### Option 2: Using Registration Forms
1. **Patient**: Go to `/register/patient/`
   - Fill in all required fields
   - Create username and password
   - Auto-creates patient profile

2. **Doctor**: Go to `/register/doctor/`
   - Fill in professional details
   - Create username and password
   - Auto-creates doctor profile

---

## 📁 Key File Locations

### Models
- `clinic/models.py` - All database models

### Views & Logic
- `clinic/views.py` - All view functions

### Forms
- `clinic/forms.py` - All forms

### Templates
- `clinic/templates/clinic/` - All HTML templates

### Admin Configuration
- `clinic/admin.py` - Admin panel setup

### Database
- `db.sqlite3` - SQLite database file

---

## 🔧 Troubleshooting

### Issue: Database errors
**Solution**:
```bash
python manage.py migrate
```

### Issue: Static files not loading
**Solution**:
```bash
python manage.py collectstatic
```

### Issue: Port 8000 already in use
**Solution**:
```bash
python manage.py runserver 8001
# Use a different port
```

### Issue: "Table doesn't exist" error
**Solution**:
```bash
python manage.py migrate
```

---

## 📊 Common Workflows

### 1. Create a Test Report for Patient
1. Login to `/admin/`
2. Go to "Test Reports"
3. Click "Add Test Report"
4. Select patient and test type
5. Upload report file
6. Set status and save
7. Patient can view in dashboard

### 2. Patient Viewing Medical History
1. Patient logs in
2. Click "Medical History" button
3. Use tabs to browse different information
4. Click "View" or "Download" for details

### 3. Doctor Updating Profile
1. Doctor logs in
2. Click "Edit Profile" or go to `/profile/update/doctor/`
3. Update information
4. Save changes

### 4. Admin Managing Pharmacy
1. Login to `/admin/`
2. Go to "Pharmacy Inventory"
3. Add medicines or edit existing ones
4. Check for expired items and reorder alerts
5. Update quantities as medicines are used

---

## 📱 Responsive Design

All pages are mobile-responsive using Bootstrap 5:
- Works on desktop, tablet, and mobile
- Touch-friendly buttons and forms
- Responsive tables and layouts

---

## 🎨 UI Features

- **Modern Design**: Bootstrap 5 with custom styling
- **Icons**: Bootstrap Icons for visual elements
- **Status Badges**: Color-coded status indicators
  - Green: Completed/Success
  - Red: Cancelled/Danger
  - Yellow: Pending/Warning
  - Blue: Active/Primary

---

## 📞 Support & Contact

For questions or issues:
1. Check the `IMPLEMENTATION_GUIDE.md` for detailed documentation
2. Review code comments in relevant files
3. Check Django documentation: https://docs.djangoproject.com/

---

## 🎉 You're All Set!

The dental clinic management system is ready to use. Start by:
1. Creating an admin account
2. Registering doctors and patients
3. Using the admin panel to manage medical records
4. Let patients access their medical history

Enjoy using Dr. Annops Dental Clinic! 🦷
