# send_mail/views.py
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor

# Initialize a thread pool executor
executor = ThreadPoolExecutor(max_workers=5)


def send_email(subject, recipient_email, context):
    # Render the HTML email template
    html_content = render_to_string("send_email/email_template.html", context)

    # Create email object
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=f"RentHome <{settings.EMAIL_HOST_USER}>",
        to=[recipient_email],
    )

    # Set email content type to HTML
    email.content_subtype = "html"

    # Send email in a separate thread
    executor.submit(email.send)
