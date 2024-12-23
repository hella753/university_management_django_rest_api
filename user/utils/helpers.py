from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.mail import EmailMessage
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


def validate_passwords(new_password, confirm_password):
    """
    This function is used to validate the passwords.
    :param new_password: password
    :param confirm_password: confirm password
    """
    if new_password != confirm_password:
        raise serializers.ValidationError("Passwords do not match.")
    try:
        validate_password(new_password)
    except ValidationError as e:
        raise serializers.ValidationError({"password": list(e.messages)})


def send_reset_email(recipient_list, url):
    """
    This function is used to email to the user with a
    link to reset their password.
    :param recipient_list: recipient email addresses
    :param url: link to reset password
    """
    mail = EmailMessage(
        subject="Reset Password",
        body="You have requested to reset your password. "
             "Click the link below to reset your password.\n"
                f"{url}",
        from_email=settings.EMAIL_HOST_USER,
        to=recipient_list
    )
    mail.send(fail_silently=False)
