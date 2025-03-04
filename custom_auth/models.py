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

    def __str__(self):
        return self.username
