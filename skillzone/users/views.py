import logging
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
from .serializers import UserSerializer, ProfileSerializer, UserRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email, ValidationError
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from .utils import handle_avatar_upload, send_verification_email
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from rest_framework.views import APIView
from .permissions import IsEmailVerified

logger = logging.getLogger(__name__)

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
    return Response({"message": "Welcome to Skillzone API!"})
        
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    logger.info(f"Starting registration process with data: {request.data}")
    
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        logger.info("Created serializer")
        
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response({
                'status': False,
                'message': 'Validation error',
                'data': None,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        logger.info("Data validated successfully")

        if not validated_data.get('accept_terms'):
            logger.warning("Terms not accepted")
            return Response({
                'status': False,
                'message': 'Terms must be accepted',
                'data': None,
                'errors': {
                    'accept_terms': ['Terms must be accepted.']
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Remove non-user fields
            user_data = validated_data.copy()
            user_data.pop('password2', None)
            user_data.pop('accept_terms', None)
            password = user_data.pop('password', None)
            
            logger.info(f"Creating user with data: {user_data}")
            
            # Create user
            user = User.objects.create_user(
                password=password,
                **user_data
            )
            logger.info(f"User created successfully with ID: {user.id}")

            # Send verification email
            try:
                send_verification_email(user)
                logger.info("Verification email sent successfully")
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}", exc_info=True)
                return Response({
                    "status": False,
                    "message": "Registration successful but failed to send verification email",
                    "errors": {"email": str(e)}
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'status': True,
                'message': 'Registration successful. Please check your email for verification code.',
                'data': {
                    'email': user.email,
                    'requires_verification': True
                },
                'errors': None
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return Response({
            'status': False,
            'message': 'An error occurred during registration',
            'data': None,
            'errors': {'detail': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        identifier = request.data.get('email') or request.data.get('username')
        password = request.data.get('password')

        if not identifier or not password:
            return Response({
                'status': False,  # Changed from 'success' to 'status'
                'message': 'Email/username and password are required',
                'data': None,
                'errors': {'validation': ['Email/username and password are required']}
            }, status=status.HTTP_400_BAD_REQUEST)

        # First try to get user by email
        try:
            user = User.objects.get(email=identifier)
        except User.DoesNotExist:
            # If not found by email, try username
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                return Response({
                    'status': False,
                    'message': 'Invalid credentials',
                    'data': None,
                    'errors': {'credentials': ['Invalid credentials']}
                }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({
                'status': False,
                'message': 'Invalid credentials',
                'data': None,
                'errors': {'credentials': ['Invalid credentials']}
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if email is verified
        if not user.profile.email_verified:
            try:
                send_verification_email(user)
                return Response({
                    'status': False,
                    'message': 'Email not verified. A new verification code has been sent.',
                    'data': {
                        'requires_verification': True,
                        'email': user.email
                    },
                    'errors': {'verification': ['Email not verified']}
                }, status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                return Response({
                    'status': False,
                    'message': 'Failed to send verification email',
                    'data': None,
                    'errors': {'email': [str(e)]}
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Email is verified, proceed with login
        refresh = RefreshToken.for_user(user)
        return Response({
            'status': True,
            'message': 'Login successful',
            'data': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            },
            'errors': None
        })

    except Exception as e:
        return Response({
            'status': False,
            'message': 'Login failed',
            'data': None,
            'errors': {'detail': str(e)}
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
            "success": False,
            "message": "Invalid points value",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

    profile = request.user.profile
    profile.points += points_to_add
    profile.save()

    serializer = ProfileSerializer(profile)
    return Response({
        "success": True,
        "message": "Points updated successfully",
        "data": serializer.data
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
        if not refresh_token:
            return Response({
                'status': False,
                'message': 'Refresh token is required',
                'data': None,
                'errors': {'refresh_token': ['This field is required']}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            profile = request.user.profile
            if profile.device_token:
                profile.device_token = None
                profile.save()

            return Response({
                'status': True,
                'message': 'Successfully logged out',
                'data': None,
                'errors': None
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({
                'status': False,
                'message': 'Invalid or expired refresh token',
                'data': None,
                'errors': {'refresh_token': ['Invalid or expired token']}
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'status': False,
            'message': 'An error occurred during logout',
            'data': None,
            'errors': {'detail': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:
        user = request.user
        profile = user.profile
        
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        user.save()
        
        if 'bio' in request.data:
            profile.bio = request.data['bio']
        if 'notification_preferences' in request.data:
            profile.notification_preferences = request.data['notification_preferences']
        profile.save()
        
        serializer = ProfileSerializer(profile)
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Handle password reset request"""
    email = request.data.get('email', '').lower().strip()
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        reset_url = request.build_absolute_uri(
            reverse('password-reset-confirm', args=[uid, token])
        )
        
        send_mail(
            'Password Reset Request',
            f'Click here to reset your password: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return Response({
            'success': True,
            'message': 'Password reset email sent'
        })
        
    except User.DoesNotExist:
        return Response({
            'success': True,  # Don't reveal if email exists
            'message': 'If an account exists with this email, a password reset link has been sent.'
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_account(request):
    """Deactivate user account"""
    try:
        user = request.user
        profile = user.profile
        
        # Require password confirmation
        password = request.data.get('password')
        if not user.check_password(password):
            return Response({
                'success': False,
                'message': 'Invalid password'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            profile.account_deactivated = True
            profile.deactivation_date = timezone.now()
            profile.save()
            
            user.is_active = False
            user.save()
            
            # Blacklist all refresh tokens
            RefreshToken.for_user(user).blacklist()
            
        return Response({
            'success': True,
            'message': 'Account deactivated successfully'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_avatar(request):
    """Update user's profile avatar"""
    try:
        if 'avatar' not in request.FILES:
            return Response({
                'success': False,
                'message': 'No image file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        image_file = request.FILES['avatar']
        profile = request.user.profile
        
        # Delete old avatar if exists
        if profile.avatar:
            if os.path.exists(profile.avatar.path):
                os.remove(profile.avatar.path)
        
        # Process and save new avatar
        avatar_path = handle_avatar_upload(image_file, request.user.id)
        profile.avatar = avatar_path
        profile.save()
        
        return Response({
            'success': True,
            'message': 'Avatar updated successfully',
            'data': {
                'avatar_url': request.build_absolute_uri(profile.avatar.url)
            }
        })
        
    except ValueError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Error updating avatar'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify email with 4-digit code"""
    try:
        code = request.data.get('code', '').strip().upper()
        email = request.data.get('email', '').strip().lower()
        
        if not code or not email:
            return Response({
                'status': False,  # Changed from 'success' to 'status' for consistency
                'message': 'Both email and verification code are required',
                'data': None,
                'errors': {'validation': ['Email and code are required']}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if user.profile.is_verification_code_valid(code):
                user.profile.email_verified = True
                user.profile.save()
                
                # Generate tokens after verification
                refresh = RefreshToken.for_user(user)
                return Response({
                    'status': True,
                    'message': 'Email verified successfully',
                    'data': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data
                    },
                    'errors': None
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': False,
                    'message': 'Invalid or expired verification code',
                    'data': None,
                    'errors': {'code': ['Invalid or expired verification code']}
                }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                'status': False,
                'message': 'User not found',
                'data': None,
                'errors': {'email': ['User not found']}
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'status': False,
            'message': 'Verification failed',
            'data': None,
            'errors': {'detail': str(e)}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64, token):
    """
    Confirm password reset and set new password
    """
    try:
        # Decode the user id
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        
        # Verify the token
        if not default_token_generator.check_token(user, token):
            return JsonResponse({
                'success': False,
                'message': 'Invalid or expired password reset token'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the new password from request data
        new_password = request.data.get('new_password')
        if not new_password:
            return JsonResponse({
                'success': False,
                'message': 'New password is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(new_password)
        user.save()

        return JsonResponse({
            'success': True,
            'message': 'Password has been reset successfully'
        })

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return JsonResponse({
            'success': False,
            'message': 'Invalid password reset link'
        }, status=status.HTTP_400_BAD_REQUEST)
        
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Validate passwords match
        if request.data.get('password') != request.data.get('password2'):
            return Response({
                'success': False,
                'message': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate terms acceptance
        if not request.data.get('accept_terms'):
            return Response({
                'success': False,
                'message': 'Terms must be accepted'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            profile = Profile.objects.get(verification_token=token)
            if not profile.email_verified:
                profile.email_verified = True
                profile.save()
                return Response({
                    'success': True,
                    'message': 'Email verified successfully'
                })
            return Response({
                'success': False,
                'message': 'Email already verified'
            })
        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid verification token'
            }, status=status.HTTP_400_BAD_REQUEST)
