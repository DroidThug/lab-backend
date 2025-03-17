import uuid
from django.db import models, transaction
from django.db.models import Max
from django.utils import timezone

class LabOrder(models.Model):
    order_id = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    patient_name = models.CharField(max_length=255, default='NA', db_index=True)
    ip_number = models.CharField(max_length=50, default='NA', db_index=True)
    age = models.PositiveIntegerField(default=0, db_index=True)
    ageunit = models.CharField(max_length=1, choices=[('y', 'Years'), ('m', 'Months'), ('d', 'Days')], default='y', db_index=True)
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], default='M', db_index=True)
    department = models.CharField(max_length=255, default='GWH', db_index=True)
    unit = models.CharField(max_length=255, default='OTHER', db_index=True)
    ipop = models.CharField(max_length=2, choices=[('ip', 'Inpatient'), ('op', 'Outpatient')], default='ip', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=50, choices=[
        ("pending", "Pending"), 
        ("accepted", "Accepted"), 
        ("rejected", "Rejected"), 
        ("flagged", "Flagged"),
        ("billing", "Billing"),
        ("rejected_from_lab", "Rejected From Lab")
    ], default='pending', db_index=True)
    tests = models.ManyToManyField('LabTest', related_name='orders')
    teststatus = models.ManyToManyField('LabTest', through='TestStatus', related_name='status_orders')
    all_tests_status = models.BooleanField(default=True, help_text="Indicates if the status applies to all tests")
    clinical_history = models.TextField(default='')
    username = models.CharField(max_length=255, default='', db_index=True)
    role = models.CharField(max_length=255, default='')
    lab_note = models.TextField(blank=True, default='')  # Keep for backward compatibility, will remove in next migration

    def save(self, *args, **kwargs):
        if not self.order_id:
            max_attempts = 10
            attempt = 0
            while attempt < max_attempts:
                try:
                    with transaction.atomic():
                        current_year = timezone.now().strftime('%y')
                        year_prefix = f'OR{current_year}'
                        
                        # Get the maximum number used this year with proper parsing
                        last_order = (LabOrder.objects
                                    .filter(order_id__startswith=year_prefix)
                                    .order_by('-order_id')
                                    .first())
                        
                        if last_order:
                            try:
                                # Extract the numerical part after OR{year}-
                                last_number = int(last_order.order_id[7:])
                                new_number = last_number + 1
                            except (ValueError, IndexError):
                                new_number = 1
                        else:
                            new_number = 1
                        
                        # Use 6-digit zero-padding for the sequential number (allows up to 999999 orders per year)
                        new_order_id = f'OR{current_year}-{new_number:06d}'  # Pad with zeros for consistent length
                        
                        # Double-check if this ID already exists
                        if not LabOrder.objects.filter(order_id=new_order_id).exists():
                            self.order_id = new_order_id
                            super().save(*args, **kwargs)
                            return
                    
                    attempt += 1
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise Exception(f"Failed to generate unique order_id after {max_attempts} attempts") from e
            
            raise Exception("Could not generate a unique order ID")
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} for {self.patient_name}"

class LabComment(models.Model):
    """Model for tracking comments/notes on lab orders with user information and timestamps"""
    order = models.ForeignKey('LabOrder', on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    username = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lab Comment'
        verbose_name_plural = 'Lab Comments'
    
    def __str__(self):
        return f"Comment by {self.username} on {self.order.order_id}"

class TestStatus(models.Model):
    """Intermediate model for tracking status of individual tests within an order"""
    order = models.ForeignKey('LabOrder', on_delete=models.CASCADE, related_name='test_statuses')
    test = models.ForeignKey('LabTest', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[
        ("pending", "Pending"), 
        ("accepted", "Accepted"), 
        ("rejected", "Rejected"), 
        ("flagged", "Flagged"),
        ("billing", "Billing"),
        ("rejected_from_lab", "Rejected From Lab")
    ], default='pending')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('order', 'test')
        verbose_name_plural = 'Test Statuses'

    def __str__(self):
        return f"{self.test.name} - {self.status}"

class LabTest(models.Model):
    name = models.CharField(max_length=255)
    privilege = models.PositiveIntegerField(choices=[(1, 'Intern'), (2, 'Postgraduate'), (3, 'Staff')], default=1)
    vac_col = models.CharField(max_length=255, default='')
    comp = models.ForeignKey('LabTest', on_delete=models.CASCADE, related_name='related_tests', null=True, blank=True)
    section = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name

class Privilege(models.Model):
    name = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return str(self.name)