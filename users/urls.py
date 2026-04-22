from django.urls import path

from .views import (
    AddUserSkillView,
    EducationView,
    ExperienceView,
    ForgotPasswordView,
    GoogleLoginView,
    LoginView,
    NotificationView,
    PortfolioView,
    ProfileView,
    RegisterView,
    ResetPasswordView,
    SkillView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/<uidb64>/<token>/", ResetPasswordView.as_view()),
    # path("verify-email/<uidb64>/<token>/", VerifyEmailView.as_view()),
    path("google-login/", GoogleLoginView.as_view()),
    path("skills/", SkillView.as_view()),
    path("add-skill/", AddUserSkillView.as_view()),
    path("portfolio/", PortfolioView.as_view()),
    path("education/", EducationView.as_view()),
    path("experience/", ExperienceView.as_view()),
    path("notifications/", NotificationView.as_view()),
    path("notifications/<int:pk>/", NotificationView.as_view()),
]
