from django.urls import path
from .views import *

urlpatterns = [
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', OTPLoginView.as_view(), name='otp-login'),
    path('forgot_password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('reset_password_validate/<uidb64>/<token>/', resetpassword_validate, name='resetpassword_validate'),
    path('reset_password/', ResetPasswordAPIView.as_view(), name='reset-password'),


]