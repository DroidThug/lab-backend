from rest_framework import viewsets, filters
from .models import Patient
from .serializers import PatientSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'ip_number'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'ip_number', 'department']