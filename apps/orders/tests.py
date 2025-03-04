from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import LabOrder, LabTest

class LabOrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.lab_test = LabTest.objects.create(name='Test 1', description='Test 1 description', price=100.00)
        self.valid_payload = {
            'patient': {
                'name': 'John Doe',
                'ip_number': '123456',
                'age': 45,
                'department': 'Medicine',
                'unit': 'GWH-MED-A'
            },
            'tests': [self.lab_test.id],
            'status': 'pending'
        }

    def test_create_lab_order(self):
        response = self.client.post('/orders/submit_order/', self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LabOrder.objects.count(), 1)
        self.assertEqual(LabOrder.objects.get().patient_name, 'John Doe')

    def test_create_lab_order_invalid(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload['patient']['ip_number'] = ''  # ip_number is required
        response = self.client.post('/orders/submit_order/', invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status(self):
        lab_order = LabOrder.objects.create(
            patient_name='John Doe',
            ip_number='123456',
            age=45,
            department='Medicine',
            unit='GWH-MED-A',
            status='pending'
        )
        response = self.client.patch(f'/orders/update_order_status/{lab_order.order_id}/', {'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lab_order.refresh_from_db()
        self.assertEqual(lab_order.status, 'completed')

class OrderIDGenerationTestCase(TestCase):
    def test_concurrent_order_generation(self):
        from concurrent.futures import ThreadPoolExecutor
        from functools import partial
        import threading
        
        def create_order():
            order = LabOrder(
                patient_name="Test Patient",
                ip_number="IP123",
                age=25
            )
            order.save()
            return order.order_id
        
        # Test concurrent order creation
        with ThreadPoolExecutor(max_workers=10) as executor:
            order_ids = list(executor.map(lambda x: create_order(), range(20)))
            
        # Verify uniqueness
        self.assertEqual(len(order_ids), len(set(order_ids)), "Duplicate order IDs were generated")
        
        # Verify format
        current_year = timezone.now().strftime('%y')
        for order_id in order_ids:
            self.assertTrue(order_id.startswith(f'OR{current_year}'), f"Invalid order ID format: {order_id}")
            self.assertTrue(order_id[4:].isdigit(), f"Invalid order ID number part: {order_id}")