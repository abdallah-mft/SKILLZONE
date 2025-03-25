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
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email, ValidationError
from django.db import transaction


@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
    return Response({"message": "Welcome to Skillzone API!"})
        
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Registers a new user with enhanced validation"""
    try:
        email = request.data.get('email', '').lower().strip()
        username = request.data.get('username', '').strip()
        password = request.data.get('password')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()

        # Enhanced validation
        errors = {}
        
        # Email validation
        if not email:
            errors['email'] = 'Email is required'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered'
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = 'Invalid email format'

        # Username validation
        if not username:
            errors['username'] = 'Username is required'
        elif len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists'

        # Password validation
        if not password:
            errors['password'] = 'Password is required'
        elif len(password) < 8:
            errors['password'] = 'Password must be at least 8 characters'
        elif not any(c.isdigit() for c in password):
            errors['password'] = 'Password must contain at least one number'
        elif not any(c.isupper() for c in password):
            errors['password'] = 'Password must contain at least one uppercase letter'

        if errors:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create user with transaction
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Profile is created by signal
            profile = user.profile
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Registration successful',
                'data': {
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    },
                    'user': ProfileSerializer(profile).data
                }
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Logs in a user using email or username and password"""
    try:
        # Accept either email or username field
        identifier = request.data.get('email') or request.data.get('username')
        password = request.data.get('password')

        if not identifier or not password:
            return Response({
                "success": False,
                "message": "Email/username and password are required",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Try to get user by email first, then username if email fails
        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "User not found",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

        # Authenticate user
        authenticated_user = authenticate(username=user.username, password=password)
        
        if authenticated_user:
            refresh = RefreshToken.for_user(authenticated_user)
            profile = get_object_or_404(Profile, user=authenticated_user)
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

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile information"""
    try:
        user = request.user
        profile = user.profile
        
        # Update basic user info
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
            
        # Update email with validation
        if 'email' in request.data:
            new_email = request.data['email'].lower().strip()
            if new_email != user.email:
                if User.objects.filter(email=new_email).exists():
                    return Response({
                        'success': False,
                        'message': 'Email already exists',
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
                try:
                    validate_email(new_email)
                    user.email = new_email
                except ValidationError:
                    return Response({
                        'success': False,
                        'message': 'Invalid email format',
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update profile fields
        if 'bio' in request.data:
            profile.bio = request.data['bio']
            
        if 'notification_preferences' in request.data:
            profile.notification_preferences.update(
                request.data['notification_preferences']
            )
            
        # Handle avatar upload
        if 'avatar' in request.FILES:
            if profile.avatar:
                profile.avatar.delete()  # Delete old avatar
            profile.avatar = request.FILES['avatar']
        
        # Save changes
        with transaction.atomic():
            user.save()
            profile.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': ProfileSerializer(profile).data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password with validation"""
    try:
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response({
                'success': False,
                'message': 'Both current and new password are required',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Verify current password
        if not user.check_password(current_password):
            return Response({
                'success': False,
                'message': 'Current password is incorrect',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Validate new password
        if len(new_password) < 8:
            return Response({
                'success': False,
                'message': 'Password must be at least 8 characters',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Generate new tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Password changed successfully',
            'data': {
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e),
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
