from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.LabOrderViewSet, basename='orders')
router.register(r'tests', views.LabTestViewSet, basename='tests')
router.register(r'comments', views.LabCommentViewSet, basename='comments')

urlpatterns = [
    path('', include(router.urls)),
    path('submit-order/', views.submit_order, name='submit-order'),
    path('orders/<str:order_id>/update-status/', views.update_order_status, name='update-order-status'),
]