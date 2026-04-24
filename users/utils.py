import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings


def send_verify_email(to_email, verify_link):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    subject = "Email Verification"
    html_content = f"""
    <h2>Verify your account</h2>
    <p>Click the link below:</p>
    <a href="{verify_link}">{verify_link}</a>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": "abdumannonovxurshid0625@gmail.com"},  # 👈 shu sender
        subject=subject,
        html_content=html_content,
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Email error:", e)