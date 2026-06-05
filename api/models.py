from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    USER_TYPES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
        ('receptionist', 'Receptionist'),
        ('pharmacist', 'Pharmacist'),
    )

    usertype = models.CharField(max_length=20, choices=USER_TYPES)

    phone = models.CharField(max_length=15, null=True, blank=True)

    address = models.TextField(null=True, blank=True)

    profile_photo = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )

    def _str_(self):
        return self.username