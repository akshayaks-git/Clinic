# Installation & Setup Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Quick Setup](#quick-setup)
4. [Running the Application](#running-the-application)
5. [First Time Setup](#first-time-setup)
6. [Troubleshooting](#troubleshooting)

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk Space**: 500MB free space
- **Browser**: Any modern browser (Chrome, Firefox, Safari, Edge)

## Installation Steps

### Option 1: Automated Setup (Recommended)

#### For Windows:
1. Open Command Prompt (`cmd.exe`)
2. Navigate to the project directory:
   ```bash
   cd path\to\dental_clinic
   ```
3. Run the setup script:
   ```bash
   setup.bat
   ```
4. Follow the prompts to create a superuser account

#### For macOS/Linux:
1. Open Terminal
2. Navigate to the project directory:
   ```bash
   cd path/to/dental_clinic
   ```
3. Make the script executable:
   ```bash
   chmod +x setup.sh
   ```
4. Run the setup script:
   ```bash
   ./setup.sh
   ```
5. Follow the prompts to create a superuser account

---

### Option 2: Manual Setup

#### Step 1: Install Python
- Download Python 3.8+ from https://www.python.org/downloads/
- **Windows**: Run the installer and **check "Add Python to PATH"**
- **macOS/Linux**: Use Homebrew or download the installer

#### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run Migrations
```bash
python manage.py migrate
```

#### Step 5: Create Superuser
```bash
python manage.py createsuperuser
```
Fill in:
- Username: (your choice)
- Email: your@email.com
- Password: (choose a secure password)
- Password confirmation

---

## Quick Setup

If you just want to get started quickly with demo data:

```bash
# 1. Setup virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Or macOS/Linux
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Populate sample data
python manage.py shell < populate_data.py

# 5. Create admin user
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

**Demo Credentials:**
- Doctor: `dr_smith` / `DoctorPass123!`
- Patient: `john_doe` / `PatientPass123!`

---

## Running the Application

### Start the Development Server

**Windows:**
```bash
# Activate virtual environment (if not already activated)
venv\Scripts\activate

# Start server
python manage.py runserver
```

**macOS/Linux:**
```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Start server
python manage.py runserver
```

You should see output like:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Access the Application

Open your browser and visit:
- **Home**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Login**: http://localhost:8000/login/

### Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## First Time Setup

### 1. Create Admin Account

After running the server, create your admin account:
```bash
python manage.py createsuperuser
```

### 2. Access Admin Panel

Visit: http://localhost:8000/admin/
- Log in with your superuser credentials
- You can now manage doctors, patients, and appointments

### 3. Create Test Data

**Option A: Using the populate script**
```bash
python manage.py shell < populate_data.py
```

**Option B: Manually via Admin Panel**
1. Go to Admin Panel
2. Click "Add Doctor"
3. Create test doctor account
4. Click "Add Patient"
5. Create test patient account

### 4. Test the Application

**As Patient:**
1. Go to http://localhost:8000/
2. Click "Register as Patient"
3. Fill in the form and submit
4. Log in with your credentials
5. Browse doctors and book an appointment

**As Doctor:**
1. Go to http://localhost:8000/
2. Click "Register as Doctor"
3. Fill in professional details
4. Log in with your credentials
5. View and confirm patient appointments

---

## Troubleshooting

### Problem: "Command 'python' not found" or "Python not installed"

**Solution:**
- Install Python from https://www.python.org/
- On Windows, ensure "Add Python to PATH" is checked during installation
- Restart your terminal/command prompt after installation
- On macOS/Linux, use `python3` instead of `python`

### Problem: "Permission denied" when running setup.sh

**Solution (macOS/Linux):**
```bash
chmod +x setup.sh
./setup.sh
```

### Problem: "ModuleNotFoundError: No module named 'django'"

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Then install requirements
pip install -r requirements.txt
```

### Problem: "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt
pip install django==4.2.13
pip install djangorestframework==3.14.0
pip install django-filter==23.5
pip install django-cors-headers==4.3.1
pip install Pillow==10.0.0
```

### Problem: Database errors or "table doesn't exist"

**Solution:**
```bash
python manage.py migrate
python manage.py makemigrations
python manage.py migrate
```

### Problem: "Port 8000 already in use"

**Solution:**
```bash
# Use a different port
python manage.py runserver 8001

# Or find and kill the process using port 8000
# Windows (in Admin Command Prompt)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Problem: "Static files not loading" (CSS/Images not showing)

**Solution:**
```bash
python manage.py collectstatic --noinput
```

### Problem: Media files not uploading or displaying

**Solution:**
1. Check that `/media/` directory exists
2. Ensure proper permissions on the directory
3. Check `settings.py` has correct `MEDIA_URL` and `MEDIA_ROOT`

### Problem: Can't log in or "Session expired"

**Solution:**
- Clear browser cookies for localhost
- Restart the development server
- Try a different browser
- Check that `DEBUG=True` in settings.py

### Problem: Admin panel not working

**Solution:**
```bash
# Create a new superuser
python manage.py createsuperuser

# Try accessing with the new credentials
```

### Problem: Changes not reflected after code edit

**Solution:**
- Restart the development server: `Ctrl+C` and `python manage.py runserver`
- For template changes, a simple refresh usually works
- Clear browser cache if needed

---

## Next Steps

After successful installation:

1. **Customize the Clinic Name**
   - Go to Admin > Clinic
   - Edit clinic information

2. **Add Your Doctors**
   - Go to Admin > Doctors
   - Add your actual doctors or register via "Register as Doctor"

3. **Customize Colors**
   - Edit `/clinic/templates/clinic/base.html`
   - Modify the `:root` variables in the style section

4. **Set Up Email Notifications**
   - Update `settings.py` with SMTP configuration

5. **Deploy to Production**
   - See README.md for deployment instructions

---

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the full [README.md](README.md)
3. Check Django documentation: https://docs.djangoproject.com/
4. Check console output for error messages
5. Verify all dependencies are installed: `pip list`

---

**Enjoy using Dr. Annops Dental Clinic Management System! 🦷**
