from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabOrderViewSet, LabTestViewSet, submit_order, update_order_status

router = DefaultRouter()
router.register(r'orders', LabOrderViewSet, basename='orders')
router.register(r'tests', LabTestViewSet, basename='tests')

urlpatterns = [
    path('', include(router.urls)),
    path('submit-order/', submit_order, name='submit-order'),
    path('orders/<str:order_id>/update-status/', update_order_status, name='update-order-status'),
]