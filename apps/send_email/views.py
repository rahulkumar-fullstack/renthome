from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import asyncio


# Define an async function to send email
async def send_email(subject, recipient_email, context):
    # Render HTML email template
    html_content = render_to_string("send_email/email_template.html", context)

    # Create the email body and subject
    email_subject = subject
    email_body = html_content
    from_email = f"RentHome <{settings.EMAIL_HOST_USER}>"

    # Send email asynchronously using Django's async-compatible send_mail function
    await asyncio.to_thread(
        send_mail,
        email_subject,
        email_body,
        from_email,
        [recipient_email],
        html_message=email_body,
    )
