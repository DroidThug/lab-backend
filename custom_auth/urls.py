from django.urls import path
from .views import (
    login_view, logout_view, user_view, 
    UserListCreateView, UserRetrieveUpdateDestroyView, 
    admin_reset_password, request_password_reset,
    confirm_password_reset, change_password,
    direct_reset_password, get_user_details_view,
    list_all_users
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user/', user_view, name='user'),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-retrieve-update-destroy'),
    path('reset-password/', admin_reset_password, name='admin-reset-password'),
    path('request-password-reset/', request_password_reset, name='request-password-reset'),
    path('reset-password-confirm/<str:uidb64>/<str:token>/', confirm_password_reset, name='confirm-password-reset'),
    path('change-password/', change_password, name='change-password'),
    path('direct-reset-password/', direct_reset_password, name='direct-reset-password'),
    path('user-details/', get_user_details_view, name='user-details'),
    path('user-details/<int:user_id>/', get_user_details_view, name='user-details-by-id'),
    path('all-users/', list_all_users, name='list-all-users'),
]