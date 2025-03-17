from rest_framework import serializers
from .models import LabOrder, LabTest, Privilege, TestStatus
from django.db import transaction

class TestStatusSerializer(serializers.ModelSerializer):
    test_id = serializers.PrimaryKeyRelatedField(source='test', queryset=LabTest.objects.all())
    test_name = serializers.StringRelatedField(source='test', read_only=True)
    
    class Meta:
        model = TestStatus
        fields = ['test_id', 'test_name', 'status', 'updated_at']

class LabOrderSerializer(serializers.ModelSerializer):
    tests = serializers.PrimaryKeyRelatedField(queryset=LabTest.objects.all(), many=True)
    patient = serializers.JSONField(write_only=True)
    patient_details = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField()
    role = serializers.CharField()
    lab_note = serializers.CharField(required=False, allow_blank=True)
    clinical_history = serializers.CharField(required=False, allow_blank=True)
    all_tests_status = serializers.BooleanField(required=False, default=True)
    test_statuses = TestStatusSerializer(source='teststatus', many=True, required=False, read_only=True)
    
    class Meta:
        model = LabOrder
        fields = ['order_id', 'patient', 'patient_details', 'tests', 'status', 'created_at', 
                  'username', 'role', 'clinical_history', 'lab_note', 'all_tests_status', 'test_statuses']
    
    def validate(self, data):
        if self.instance is None and ('tests' not in data or not data['tests']):
            raise serializers.ValidationError("At least one test must be specified")
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        patient_data = validated_data.pop('patient')
        tests = validated_data.pop('tests', [])
        username = validated_data.pop('username')
        role = validated_data.pop('role')
        
        # Create the order first without the tests
        lab_order = LabOrder.objects.create(
            patient_name=patient_data['name'],
            ip_number=patient_data['ip_number'],
            age=patient_data['age'],
            ageunit=patient_data.get('ageunit'),
            sex=patient_data.get('sex'),
            department=patient_data['department'],
            unit=patient_data['unit'],
            username=username,
            role=role,
            **validated_data
        )
        
        # Set the tests after the order is created and has an ID
        lab_order.tests.set(tests)
        
        # If we're setting a status, let's also create test statuses for all tests
        if lab_order.status != 'pending':
            for test in tests:
                TestStatus.objects.create(
                    order=lab_order,
                    test=test,
                    status=lab_order.status
                )
        
        return lab_order
    
    @transaction.atomic
    def update(self, instance, validated_data):
        tests = validated_data.pop('tests', None)
        status = validated_data.get('status')
        all_tests_status = validated_data.get('all_tests_status', True)
        
        if tests is not None:
            instance.tests.set(tests)
        
        # Update the model with the remaining data
        instance = super().update(instance, validated_data)
        
        # Handle test statuses if status is updated
        if status and status != 'pending':
            # If status applies to all tests, update all test statuses
            if all_tests_status:
                tests_to_update = instance.tests.all()
                for test in tests_to_update:
                    TestStatus.objects.update_or_create(
                        order=instance,
                        test=test,
                        defaults={'status': status}
                    )
        
        return instance
    
    def get_patient_details(self, obj):
        return {
            'name': obj.patient_name,
            'ip_number': obj.ip_number,
            'age': obj.age,
            'ageunit': obj.ageunit,
            'sex': obj.sex,
            'department': obj.department,
            'unit': obj.unit,
        }

class LabTestSerializer(serializers.ModelSerializer):
    privilege = serializers.IntegerField()
    comp = serializers.PrimaryKeyRelatedField(queryset=LabTest.objects.all(), allow_null=True, required=False)
    
    class Meta:
        model = LabTest
        fields = '__all__'