import os
from sib_api_v3_sdk import Configuration, ApiClient
from sib_api_v3_sdk.api import transactional_emails_api
from sib_api_v3_sdk.models import SendSmtpEmail


def send_verify_email(email, verify_link):
    configuration = Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = transactional_emails_api.TransactionalEmailsApi(ApiClient(configuration))

    send_smtp_email = SendSmtpEmail(
        to=[{"email": email}],
        sender={"email": "abdumannonovxurshid0625@gmail.com"},
        subject="Verify your email",
        html_content=f"<p>Click here: <a href='{verify_link}'>Verify</a></p>"
    )

    api_instance.send_transac_email(send_smtp_email)