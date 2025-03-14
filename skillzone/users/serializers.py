from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Level

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('name', 'min_points', 'max_points', 'badge_url')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    next_level = serializers.SerializerMethodField()
    points_to_next_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ('user', 'points', 'full_name', 'level', 'next_level', 'points_to_next_level')
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()

    def get_level(self, obj):
        current_level = obj.get_level()
        return LevelSerializer(current_level).data if current_level else None

    def get_next_level(self, obj):
        current_level = obj.get_level()
        if current_level:
            next_level = Level.objects.filter(min_points__gt=current_level.max_points).order_by('min_points').first()
            return LevelSerializer(next_level).data if next_level else None
        return None

    def get_points_to_next_level(self, obj):
        current_level = obj.get_level()
        if current_level:
            next_level = Level.objects.filter(min_points__gt=current_level.max_points).order_by('min_points').first()
            if next_level:
                return next_level.min_points - obj.points
        return 0
