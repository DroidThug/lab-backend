from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('intern', 'Intern'),
        ('postgraduate', 'Postgraduate'),
        ('staff', 'Staff'),
        ('labtech', 'Lab Technician'),
    ]
    
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.username
        
    def get_user_details(self):
        """
        Return all user details except password
        """
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'role': self.role,
            'phone_number': self.phone_number,
            'designation': self.designation,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'date_joined': self.date_joined,
            'last_login': self.last_login,
        }
