from django.db import models

class Patient(models.Model):
    ip_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=10)
    department = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.ip_number})"
