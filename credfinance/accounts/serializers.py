from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        
        password_age = timezone.now() - self.user.password_last_changed
        if password_age > timedelta(days=30):
            self.user.force_password_change = True
            self.user.save(update_fields=['force_password_change'])
        
        data.update({'user_id': self.user.id, 'force_password_change': self.user.force_password_change, 'user_type':self.user.user_type})
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token