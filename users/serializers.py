from rest_framework import serializers
from .models import User, Profile
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()




class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'full_name', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            role=validated_data['role']
        )
        return user
    


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("User not found")
        
        if not user.is_verified:
            raise ValidationError("Email not verified")

        if not user.check_password(password):
            raise ValidationError("Invalid password")

        # 🔥 TOKEN YARATISH
        refresh = RefreshToken.for_user(user)

        return {
            "user": user.email,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        

class ProfileSerializer(serializers.ModelSerializer):
     class Meta:
         model = Profile
         fields = '__all__'  
         


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("User not found")
        return data 
    
    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=6)

    def validate(self, data):
        if not User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("User not found")
        return data
