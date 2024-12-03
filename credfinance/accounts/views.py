from django.http import HttpResponse
from django.shortcuts import redirect, render
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .models import Account
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib import auth
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
import random
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from datetime import timedelta
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from utils.utils import Utils
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, AccountUpdateForm
from django.contrib import messages

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login
from django.urls import reverse

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email')
        
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Account.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            user.set_otp(otp)
            message = f"Your two-factor authentication OTP is {otp}. It will expire in 5 minutes."
            print(message)
            return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({"detail": "Account with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": "Failed to send OTP.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({"detail": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Account.objects.get(email=email)

            # Extracting the IP address
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            if user.verify_otp(otp):
                
                Utils.log_audit_trail(
                    user=request.user,
                    action="User Login",
                    model_name="Account",
                    model_id=user.id,
                    previous_value=None,
                    new_value=None,
                    ip_address=ip_address 
                )
                
                return Response({"detail": "OTP verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_401_UNAUTHORIZED)
        except Account.DoesNotExist:
            return Response({"detail": "Account with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": "Failed to verify OTP.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OTPLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        otp = request.data.get('otp')

        if not all([email, password, otp]):
            return Response(
                {"detail": "Email, password, and OTP are all required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password, otp=otp)
        if user:
            try:
                refresh = CustomTokenObtainPairSerializer.get_token(user)
                access_token = refresh.access_token
                data = {
                    'refresh': str(refresh),
                    'access': str(access_token),
                    'user_id': user.id,
                    'email': user.email,
                    'full_name': user.full_name(),
                }
                return Response(data, status=status.HTTP_200_OK)
            except TokenError as e:
                return Response({"detail": "Token generation failed.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"detail": "Invalid credentials or OTP."}, status=status.HTTP_401_UNAUTHORIZED)

class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'  
            send_email.send()

            return Response({'message': 'Password reset email has been sent to your email address.'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Account does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        return redirect(f'http://dashboard.credspace.co.zw/reset-password/{uidb64}/{token}')
    else:
        return HttpResponse('Invalid token', status=400)

    
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        new_password = request.data.get('password')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = Account.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
            return Response({'error': 'Invalid UID'}, status=status.HTTP_400_BAD_REQUEST)

        old_password = user.password
        if default_token_generator.check_token(user, token):
            user.password = make_password(new_password)
            user.save()

            # Extracting the IP address
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            Utils.log_audit_trail(
                user=user,
                action="Password Reset",
                model_name="Account",
                model_id=user.id,
                previous_value=old_password,
                new_value=user.password,  
                timestamp=timezone.now(),
                ip_address=ip_address
            )
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.userprofile)
        account_form = AccountUpdateForm(request.POST, instance=user)
        if profile_form.is_valid() and account_form.is_valid():
            profile_form.save()
            account_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile') 
        else:
            messages.error(request, 'There was an error updating your profile. Please check the fields and try again.')
    else:
        profile_form = ProfileUpdateForm(instance=user.userprofile)
        account_form = AccountUpdateForm(instance=user)

    context = {
        'profile_form': profile_form,
        'account_form': account_form,
        'user': user
    }
    return render(request, 'accounts/user-profile.html', context)



@login_required
def custom_password_change(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not old_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('profile')

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, "The old password is incorrect.")
            return redirect('profile')

        if new_password != confirm_password:
            messages.error(request, "The new password and confirm password do not match.")
            return redirect('profile')

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('profile')

        user.set_password(new_password)
        user.save()

        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        Utils.log_audit_trail(
            user=user,
            action="Password Reset",
            model_name="Account",
            model_id=user.id,
            previous_value=old_password,
            new_value=user.password,  
            ip_address=ip_address
        )

        update_session_auth_hash(request, user)
        messages.success(request, "Your password has been changed successfully.")
        return redirect('profile')

    return render(request, 'accounts/user-profile.html')



def custom_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email = email, password = password)
        if user is not None:
            auth.login(request, user)

            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            Utils.log_audit_trail(
                user=user,
                action="User Logged In",
                model_name="Account",
                model_id=user.id,
                previous_value='',
                new_value='',  
                ip_address=ip_address
            )
            next_url = request.GET.get('next', reverse('home'))
            return HttpResponseRedirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'accounts/login.html')

def custom_logout(request):
    logout(request)  
    return redirect('login')