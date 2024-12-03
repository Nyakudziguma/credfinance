from django.urls import path
from django.contrib.auth import views as auth_views

from .views import *

urlpatterns = [
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('forgot_password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset_password_validate/<uidb64>/<token>/', resetpassword_validate, name='resetpassword_validate'),
    path('reset_password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path('profile', profile, name='profile'),
    path('change-password/', custom_password_change , name='change_password'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
]


