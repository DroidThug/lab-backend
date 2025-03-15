from rest_framework import serializers
from .models import LabOrder, LabTest, Privilege
from django.db import transaction

class LabOrderSerializer(serializers.ModelSerializer):
    tests = serializers.PrimaryKeyRelatedField(queryset=LabTest.objects.all(), many=True)
    patient = serializers.JSONField(write_only=True)
    patient_details = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField()
    role = serializers.CharField()
    lab_note = serializers.CharField(required=False, allow_blank=True)
    clinical_history = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = LabOrder
        fields = ['order_id', 'patient', 'patient_details', 'tests', 'status', 'created_at', 'username', 'role', 'clinical_history', 'lab_note']

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
        
        return lab_order

    def update(self, instance, validated_data):
        tests = validated_data.pop('tests', None)
        if tests is not None:
            instance.tests.set(tests)
        return super().update(instance, validated_data)

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