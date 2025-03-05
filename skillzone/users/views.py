from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import Profile
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def index(request):
    return JsonResponse({"message": "Welcome to Skillzone API!"})


@api_view(['POST'])
def register(request):
    """Registers a new user"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    try:
        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user)  # Create a profile for the new user
        token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({"message": "User registered successfully", "token": token.key}, status=201)
    except IntegrityError:
        return JsonResponse({"error": "Username already exists"}, status=400)

@api_view(['POST'])
def login(request):
    """Logs in a user and returns a token"""
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({"message": "Login successful", "token": token.key})
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Fetches user profile details"""
    profile = get_object_or_404(Profile, user=request.user)
    return JsonResponse({"username": request.user.username, "points": profile.points})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_points(request):
    """Updates user points"""
    points_to_add = request.data.get('points', 0)

    if not isinstance(points_to_add, int) or points_to_add < 0:
        return JsonResponse({"error": "Invalid points value"}, status=400)

    request.user.profile.points += points_to_add
    request.user.profile.save()
    return JsonResponse({"message": "Points updated", "new_points": request.user.profile.points})


#  ✅✅✅✅✅✅✅  