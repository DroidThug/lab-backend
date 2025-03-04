from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import serializers
from django.db.models import Q, Count, F
from django.db.models.functions import ExtractYear
from django.db import transaction
from .models import LabOrder, LabTest
from .serializers import LabOrderSerializer, LabTestSerializer
import logging
from rest_framework.pagination import PageNumberPagination

# Configure query logging for development
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class LabOrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class LabOrderViewSet(viewsets.ModelViewSet):
    serializer_class = LabOrderSerializer
    lookup_field = 'order_id'
    pagination_class = LabOrderPagination

    def get_queryset(self):
        return LabOrder.objects.prefetch_related('tests').all()

    @action(detail=False, methods=['get'])
    def search(self, request):
        patient_name = request.query_params.get('patient_name', '')
        ip_number = request.query_params.get('ip_number', '')
        department = request.query_params.get('department', '')
        status = request.query_params.get('status', '')
        date_from = request.query_params.get('date_from', '')
        date_to = request.query_params.get('date_to', '')
        test_name = request.query_params.get('test_name', '')
        age_min = request.query_params.get('age_min', '')
        age_max = request.query_params.get('age_max', '')
        unit = request.query_params.get('unit', '')
        created_by = request.query_params.get('created_by', '')
        order_by = request.query_params.get('order_by', '-created_at')

        queryset = self.get_queryset()
        
        # Optimize query by combining OR conditions
        name_ip_filters = Q()
        if patient_name:
            name_ip_filters |= Q(patient_name__icontains=patient_name)
        if ip_number:
            name_ip_filters |= Q(ip_number__icontains=ip_number)
        if name_ip_filters:
            queryset = queryset.filter(name_ip_filters)

        # Apply AND filters
        if department:
            queryset = queryset.filter(department__iexact=department)
        if status:
            queryset = queryset.filter(status__iexact=status)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        if test_name:
            queryset = queryset.filter(tests__name__icontains=test_name)
        if age_min:
            queryset = queryset.filter(age__gte=int(age_min))
        if age_max:
            queryset = queryset.filter(age__lte=int(age_max))
        if unit:
            queryset = queryset.filter(unit__iexact=unit)
        if created_by:
            queryset = queryset.filter(username__icontains=created_by)

        # Apply distinct and ordering after all filters
        queryset = queryset.distinct()
        
        # Optimize ordering
        if order_by.startswith('-'):
            field = order_by[1:]
            queryset = queryset.order_by(F(field).desc(nulls_last=True))
        else:
            queryset = queryset.order_by(F(order_by).asc(nulls_last=True))

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get statistics about orders"""
        date_from = request.query_params.get('date_from', '')
        date_to = request.query_params.get('date_to', '')
        
        # Base queryset with date filters
        queryset = self.get_queryset()
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        # Use annotations for efficient counting
        stats = queryset.aggregate(
            total_orders=Count('id'),
            pending_orders=Count('id', filter=Q(status='pending')),
            accepted_orders=Count('id', filter=Q(status='accepted')),
            rejected_orders=Count('id', filter=Q(status='rejected')),
            flagged_orders=Count('id', filter=Q(status='flagged'))
        )
        
        # Efficient department and unit counts using values and annotation
        stats['departments'] = list(
            queryset.values('department')
                   .annotate(count=Count('id'))
                   .order_by('-count')
        )
        
        stats['units'] = list(
            queryset.values('unit')
                   .annotate(count=Count('id'))
                   .order_by('-count')
        )
        
        stats['tests_ordered'] = list(
            queryset.values('tests__name')
                   .annotate(count=Count('id'))
                   .order_by('-count')
        )
        
        return Response(stats)

@api_view(['POST'])
@transaction.atomic
def submit_order(request):
    logger.debug('submit_order action called')
    logger.debug('Request data: %s', request.data)
    try:
        data = request.data.copy()  # Make a mutable copy
        data['username'] = request.user.username
        data['role'] = request.user.role
        serializer = LabOrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        headers = {'Location': order.order_id}
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    except Exception as e:
        raise serializers.ValidationError(str(e))

@api_view(['PATCH'])
def update_order_status(request, order_id):
    try:
        order = LabOrder.objects.get(order_id=order_id)
    except LabOrder.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    status = request.data.get('status')
    lab_note = request.data.get('lab_note', '')
    if status not in ['pending', "accepted", 'rejected', 'flagged']:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    order.status = status
    order.lab_note = lab_note
    order.save()
    return Response({'status': 'Order status updated', 'lab_note': order.lab_note}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_orders(request):
    orders = LabOrder.objects.all()
    serializer = LabOrderSerializer(orders, many=True)
    return Response(serializer.data)

class LabTestViewSet(viewsets.ModelViewSet):
    serializer_class = LabTestSerializer

    def get_queryset(self):
        queryset = LabTest.objects.all().order_by('id')
        privileges = self.request.query_params.getlist('privilege', None)
        
        if privileges:
            privileges = [int(p) for p in privileges]
            queryset = queryset.filter(privilege__in=privileges)  # Fixed missing closing parenthesis
        
        return queryset.only('id', 'name', 'privilege', 'vac_col')