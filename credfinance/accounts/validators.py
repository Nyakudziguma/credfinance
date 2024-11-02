import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.hashers import check_password

class PreviousPasswordValidator:
    def __init__(self, password_history_count=3):
        self.password_history_count = password_history_count

    def validate(self, password, user=None):
        if user and user.pk:
            previous_passwords = user.passwordhistory_set.order_by('-timestamp')[:self.password_history_count]
            for old_password in previous_passwords:
                if check_password(password, old_password.password):
                    raise ValidationError(
                        _("This password has been used before."),
                        code='password_used_before',
                    )

    def get_help_text(self):
        return _(
            "Your password should not be the same as your last %d passwords." % self.password_history_count
        )
    
class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("The password must contain at least one digit."),
                code='password_no_number',
            )
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("The password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
        if not re.findall('[^a-zA-Z0-9]', password):
            raise ValidationError(
                _("The password must contain at least one special character."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one digit, one uppercase letter, "
            "one lowercase letter, and one special character."
        )