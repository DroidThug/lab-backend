from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token, rotate_token
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer, UserDetailsSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

CustomUser = get_user_model()

class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    rotate_token(request)
    csrf_token = get_token(request)
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        role = user.role  # Use the role field directly from the CustomUser model
        response = Response({'message': 'Login successful', 'token': token.key, 'role': role}, status=status.HTTP_200_OK)
        response.set_cookie('csrftoken', csrf_token)
        return response
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def user_view(request):
    if request.user.is_authenticated:
        role = request.user.role  # Use the role field directly from the CustomUser model
        return JsonResponse({'username': request.user.username, 'role': role})
    else:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_reset_password(request):
    """
    Admin function to reset a user's password
    Requires admin privileges
    """
    username = request.data.get('username')
    new_password = request.data.get('new_password')
    
    if not username or not new_password:
        return Response(
            {'error': 'Username and new password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = CustomUser.objects.get(username=username)
        user.password = make_password(new_password)
        user.save()
        
        # Invalidate any existing tokens for the user
        Token.objects.filter(user=user).delete()
        
        return Response(
            {'message': f'Password reset successful for user {username}'},
            status=status.HTTP_200_OK
        )
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Initiate the password reset process for a user
    Sends a reset link to the user's email
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = CustomUser.objects.get(email=email)
        
        # Generate token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Create reset link
        reset_link = f"{request.build_absolute_uri('/').rstrip('/')}/custom_auth/reset-password-confirm/{uid}/{token}/"
        
        # Send email with reset link
        email_subject = "Password Reset Request"
        email_message = f"""
        Hi {user.username},

        You requested a password reset. Please click the link below to reset your password:

        {reset_link}

        If you didn't make this request, please ignore this email.
        """
        
        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return Response(
            {'message': 'Password reset email sent. Please check your inbox.'},
            status=status.HTTP_200_OK
        )
    except CustomUser.DoesNotExist:
        # For security reasons, still return a success message even if the email doesn't exist
        return Response(
            {'message': 'If your email is registered, you will receive a password reset link.'},
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request, uidb64, token):
    """
    Confirm a password reset request and set the new password
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            
            if not new_password:
                return Response(
                    {'error': 'New password is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.password = make_password(new_password)
            user.save()
            
            # Invalidate existing tokens
            Token.objects.filter(user=user).delete()
            
            return Response(
                {'message': 'Password reset successful. You can now login with your new password.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Invalid or expired token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        return Response(
            {'error': 'Invalid reset link'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def change_password(request):
    """
    Allow authenticated users to change their own password
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response(
            {'error': 'Both old and new password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify old password
    user = authenticate(username=request.user.username, password=old_password)
    if user is None:
        return Response(
            {'error': 'Old password is incorrect'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.password = make_password(new_password)
    user.save()
    
    # Invalidate existing tokens
    Token.objects.filter(user=user).delete()
    
    return Response(
        {'message': 'Password changed successfully. Please login with your new password.'},
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def direct_reset_password(request):
    """
    Direct password reset without email verification.
    Requires username and security information for verification.
    """
    username = request.data.get('username')
    security_answer = request.data.get('security_answer')  # Could be any verification info
    new_password = request.data.get('new_password')
    
    if not username or not security_answer or not new_password:
        return Response(
            {'error': 'Username, security answer and new password are all required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = CustomUser.objects.get(username=username)
        
        # Here you would typically verify some security information
        # For example, compare security_answer with a stored security question answer
        # This is simplified for now - you should implement proper verification
        
        # Set the new password
        user.password = make_password(new_password)
        user.save()
        
        # Invalidate any existing tokens for the user
        Token.objects.filter(user=user).delete()
        
        return Response(
            {'message': 'Password has been reset successfully. Please login with your new password.'},
            status=status.HTTP_200_OK
        )
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details_view(request, user_id=None):
    """
    Get detailed user information (excluding password)
    If user_id is provided, get that user's details (admin or labtech only)
    Otherwise, get the authenticated user's details
    """
    if user_id:
        # Only admins and lab technicians can view other users' details
        if not (request.user.is_staff or request.user.role == 'labtech'):
            return Response(
                {'error': 'You do not have permission to view this user\'s details'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        user = request.user
    
    serializer = UserDetailsSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_users(request):
    """
    Get a list of all users with their details
    Accessible by admins and lab technicians
    """
    # Check if user is admin or lab technician
    if not (request.user.is_staff or request.user.role == 'labtech'):
        return Response(
            {'error': 'You do not have permission to view all users'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    users = CustomUser.objects.all()
    serializer = UserDetailsSerializer(users, many=True)
    return Response(serializer.data)