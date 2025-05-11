from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    accept_terms = serializers.BooleanField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    is_teacher = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'accept_terms', 'first_name', 'last_name', 'is_teacher')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate(self, data):
        errors = {}
        
        if not data.get('password'):
            errors['password'] = ['This field is required.']
        if not data.get('password2'):
            errors['password2'] = ['This field is required.']
        if not data.get('accept_terms'):
            errors['accept_terms'] = ['Terms must be accepted.']
            
        if errors:
            raise serializers.ValidationError(errors)

        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({'password': ["Passwords don't match."]})
        
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('accept_terms')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user
