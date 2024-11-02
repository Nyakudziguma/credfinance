
from django.contrib.auth.backends import ModelBackend
from .models import Account
from bot.messageFunctions import sendWhatsAppMessage
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

import random
class CustomBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Account.objects.get(email=email)
            if user.is_locked:
                raise ValueError("Your account has been blocked. Please contact the system administrator.")
            if user.check_password(password):
                otp = str(random.randint(100000, 999999))
                user.set_otp(otp)
                message = f"Your two-factor authentication OTP is {otp}. It will expire in 5 minutes."
                sendWhatsAppMessage(user.phone_number, message)
                mail_subject = 'Loggin Attempt'
                message = render_to_string('otp_email.html', {
                    'user': user,
                    'otp': otp,
                })
                to_email = user.email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                return user
        except Account.DoesNotExist:
            return None