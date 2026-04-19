from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import ForgotPasswordSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            verify_link = f"http://127.0.0.1:8000/api/verify-email/{uid}/{token}/"
            
            send_mail(
                subject="Verify your email",
                message=f"Click link: {verify_link}",
                from_email="abdumannonovxurshid0625@gmail.com",
                recipient_list=[user.email],
            )
            return Response({"message": "User created. Check your email"})

        return Response(serializer.errors, status=400)


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            return Response({"error": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid token"}, status=400)

        user.is_verified = True
        user.save()

        return Response({"message": "Email verified successfully"})
    
    
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)

        return Response(serializer.errors, status=400)
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400) 
    
    
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = f"http://127.0.0.1:8000/api/reset-password/{uid}/{token}/"

            send_mail(
                subject="Password Reset",
                message=f"Click link: {reset_link}",
                from_email="abdumannonovxurshid0625@gmail.com",
                recipient_list=[email],
            )

            return Response({"message": "Reset link sent"})

        return Response(serializer.errors, status=400)




class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            return Response({"error": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid token"}, status=400)

        new_password = request.data.get("password")

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"}) 
    

