from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token, rotate_token
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

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