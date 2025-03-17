from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import serializers
from django.db.models import Q, Count, F
from django.db.models.functions import ExtractYear
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import LabOrder, LabTest, TestStatus, LabComment
from .serializers import LabOrderSerializer, LabTestSerializer, TestStatusSerializer, LabCommentSerializer
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
        return LabOrder.objects.prefetch_related('tests', 'teststatus').all()

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
        order_id = request.query_params.get('order_id', '')
        ipop = request.query_params.get('ipop', '')

        queryset = self.get_queryset()
        
        # Filter by order_id if provided
        if order_id:
            queryset = queryset.filter(order_id__icontains=order_id)
        
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
        if ipop:
            queryset = queryset.filter(ipop__iexact=ipop)

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
        
        # Add patient type statistics (inpatient vs outpatient)
        stats['patient_types'] = list(
            queryset.values('ipop')
                   .annotate(count=Count('id'))
                   .order_by('-count')
        )
        
        return Response(stats)

    @action(detail=True, methods=['post'])
    def update_test_status(self, request, order_id=None):
        """Update status for specific tests within an order"""
        try:
            order = self.get_object()
        except LabOrder.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get parameters
        all_tests = request.data.get('all_tests_status', False)
        new_status = request.data.get('status')
        test_ids = request.data.get('test_ids', [])
        
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if new_status not in dict(TestStatus._meta.get_field('status').choices).keys():
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Update the order's overall status
            order.status = new_status
            order.all_tests_status = all_tests
            order.save()
            
            # If applying to all tests
            if all_tests:
                tests = order.tests.all()
                for test in tests:
                    TestStatus.objects.update_or_create(
                        order=order,
                        test=test,
                        defaults={'status': new_status}
                    )
            # If applying to specific tests
            elif test_ids:
                tests = LabTest.objects.filter(id__in=test_ids)
                for test in tests:
                    TestStatus.objects.update_or_create(
                        order=order,
                        test=test,
                        defaults={'status': new_status}
                    )
                    
            # Return updated test statuses
            test_statuses = TestStatus.objects.filter(order=order)
            serializer = TestStatusSerializer(test_statuses, many=True)
            
            return Response({
                'message': 'Test statuses updated successfully',
                'order_status': order.status,
                'all_tests_status': order.all_tests_status,
                'test_statuses': serializer.data
            }, status=status.HTTP_200_OK)

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
    
    new_status = request.data.get('status')
    lab_note = request.data.get('lab_note', '')
    all_tests_status = request.data.get('all_tests_status', True)
    
    if new_status not in ['pending', 'accepted', 'rejected', 'flagged', 'billing', 'rejected_from_lab']:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    order.status = new_status
    order.lab_note = lab_note
    order.all_tests_status = all_tests_status
    order.save()
    
    # If all tests status is true, update all test statuses
    if all_tests_status and new_status != 'pending':
        for test in order.tests.all():
            TestStatus.objects.update_or_create(
                order=order,
                test=test,
                defaults={'status': new_status}
            )
    
    return Response({
        'status': 'Order status updated', 
        'lab_note': order.lab_note,
        'all_tests_status': order.all_tests_status
    }, status=status.HTTP_200_OK)

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

class LabCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lab comments
    """
    queryset = LabComment.objects.all()
    serializer_class = LabCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter comments by order_id if provided in the URL parameters"""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order_id', None)
        if order_id:
            queryset = queryset.filter(order__order_id=order_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new comment, getting the lab order by order_id"""
        order_id = request.data.get('order_id')
        if not order_id:
            return Response(
                {"error": "order_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = get_object_or_404(LabOrder, order_id=order_id)
        
        # Create a mutable copy of request.data
        data = request.data.copy()
        data['order'] = order.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )