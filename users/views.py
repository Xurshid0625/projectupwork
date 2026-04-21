from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .models import Education, Experience, Notification, Portfolio, Skill, UserSkill
from .serializers import (
    EducationSerializer,
    ExperienceSerializer,
    ForgotPasswordSerializer,
    GoogleLoginSerializer,
    LoginSerializer,
    NotificationSerializer,
    PortfolioSerializer,
    ProfileSerializer,
    RegisterSerializer,
    SkillSerializer,
)

User = get_user_model()


class RegisterView(APIView):

    @swagger_auto_schema(request_body=RegisterSerializer)
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

    @swagger_auto_schema(request_body=LoginSerializer)
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

    @swagger_auto_schema(request_body=ProfileSerializer)
    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class ForgotPasswordView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
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
    
    @swagger_auto_schema(request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "password": openapi.Schema(type=openapi.TYPE_STRING)
            }
        ))
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


class GoogleLoginView(APIView):
    @swagger_auto_schema(request_body=GoogleLoginSerializer)
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data)

        return Response(serializer.errors, status=400)


class SkillView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)


class AddUserSkillView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "skill_id": openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    ))
    def post(self, request):
        skill_id = request.data.get("skill_id")

        skill = get_object_or_404(Skill, id=skill_id)

        exists = UserSkill.objects.filter(user=request.user, skill=skill).exists()

        if exists:
            return Response({"message": "Skill already added"}, status=400)

        UserSkill.objects.create(user=request.user, skill=skill)

        return Response({"message": "Skill added successfully"})


class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Portfolio.objects.filter(user=request.user)
        serializer = PortfolioSerializer(items, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=PortfolioSerializer)
    def post(self, request):
        serializer = PortfolioSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class EducationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Education.objects.filter(user=request.user)
        serializer = EducationSerializer(items, many=True)
        return Response(serializer.data)
    @swagger_auto_schema(request_body=EducationSerializer)
    def post(self, request):
        serializer = EducationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class ExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Experience.objects.filter(user=request.user)
        serializer = ExperienceSerializer(items, many=True)
        return Response(serializer.data)
    @swagger_auto_schema(request_body=ExperienceSerializer)
    def post(self, request):
        serializer = ExperienceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by(
            "-created_at"
        )
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        notif = get_object_or_404(Notification, id=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return Response({"message": "Marked as read"})
