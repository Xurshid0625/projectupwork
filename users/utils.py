from django.core.mail import send_mail
from django.conf import settings


def send_verify_email(to_email, verify_link):
    subject = "Email Verification"

    message = f"""
    Verify your account:

    {verify_link}
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
