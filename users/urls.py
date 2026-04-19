from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view()),
]