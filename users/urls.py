from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ForgotPasswordView, ResetPasswordView, VerifyEmailView, GoogleLoginView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view()),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view()),
    path('google-login/', GoogleLoginView.as_view()),
]