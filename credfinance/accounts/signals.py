from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Account

@receiver(user_logged_in)
def reset_failed_attempts(sender, user, request, **kwargs):
    user.failed_login_attempts = 0
    user.save()

@receiver(user_login_failed)
def increment_failed_attempts(sender, credentials, request, **kwargs):
    email = credentials.get('username')
    try:
        user = Account.objects.get(email=email)
        if user.failed_login_attempts >= 2: 
            user.is_locked = True
        user.failed_login_attempts += 1
        user.save()
    except Account.DoesNotExist:
        pass