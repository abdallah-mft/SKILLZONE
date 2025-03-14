from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken  # Add this import


@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
    return Response({"message": "Welcome to Skillzone API!"})
        
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Registers a new user with email, username, password, and full name"""
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')

    # Validation
    if not all([email, username, password]):
        return Response({
            "error": "Email, username, and password are required"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response({
            "error": "Email already registered"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response({
            "error": "Username already exists"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate email format
    try:
        from django.core.validators import validate_email
        validate_email(email)
    except:
        return Response({
            "error": "Invalid email format"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create user only after all validations pass
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Don't create profile here - it's created by the signal
        # Get the profile that was created by the signal
        profile = user.profile
        
        # Generate token
        token, _ = Token.objects.get_or_create(user=user)
        
        serializer = ProfileSerializer(profile)
        return Response({
            "message": "User registered successfully",
            "token": token.key,
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        # If any error occurs during user creation, delete the user
        if 'user' in locals():
            user.delete()
        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Logs in a user using email and password"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                "success": False,
                "message": "Email and password are required",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(email=email)
        user = authenticate(username=user.username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)  # Generate JWT
            profile = get_object_or_404(Profile, user=user)
            serializer = ProfileSerializer(profile)
            
            return Response({
                "success": True,
                "message": "Login successful",
                "data": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": serializer.data
                }
            })
        else:
            return Response({
                "success": False,
                "message": "Invalid credentials",
                "data": None
            }, status=status.HTTP_401_UNAUTHORIZED)

    except User.DoesNotExist:
        return Response({
            "success": False,
            "message": "User not found",
            "data": None
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e),
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Fetches user profile details"""
    profile = get_object_or_404(Profile, user=request.user)
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_points(request):
    """Updates user points"""
    points_to_add = request.data.get('points', 0)

    if not isinstance(points_to_add, (int, float)) or points_to_add < 0:
        return Response({
            "error": "Invalid points value"
        }, status=status.HTTP_400_BAD_REQUEST)

    profile = request.user.profile
    old_level = profile.get_level()
    
    profile.points += points_to_add
    profile.save()
    
    new_level = profile.get_level()
    level_changed = old_level != new_level if old_level and new_level else False

    serializer = ProfileSerializer(profile)
    return Response({
        "message": "Points updated successfully",
        "level_up": level_changed,
        "profile": serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def users_index(request):
    """API index - Lists available endpoints"""
    return JsonResponse({
        "message": "Welcome to the Users API!",
        "endpoints": {
            "register": "/api/users/register/",
            "login": "/api/users/login/",
            "profile": "/api/users/profile/",
            "update_points": "/api/users/update-points/"
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_device_token(request):
    """Updates user's device token for push notifications"""
    device_token = request.data.get('device_token')
    
    if not device_token or len(device_token.strip()) == 0:
        return Response({
            "success": False,
            "message": "Valid device token is required",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    profile = request.user.profile
    profile.device_token = device_token.strip()
    profile.save()
    
    return Response({
        "success": True,
        "message": "Device token updated successfully",
        "data": {"device_token": device_token}
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "success": True,
                "message": "Successfully logged out"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "message": "Refresh token is required"
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "success": False,
            "message": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
