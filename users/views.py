from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .serializers import UserSerializer, OTPSerializer
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.core.cache import cache
from functools import wraps
import random

def rate_limit(view_func):
    @wraps(view_func)
    def _wrapped_view(view, request, *args, **kwargs):
        email = request.data.get('email')
        cache_key = f'otp_rate_limit_{email}'
        if cache.get(cache_key):
            return Response({'error': 'OTP request limit reached. Please try again later.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)
        response = view_func(view, request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            cache.set(cache_key, True, timeout=60)  # Limit to one request per minute
        return response
    return _wrapped_view

def generate_otp():
    return random.randint(100000, 999999)

class RegisterOrLoginView(APIView):
    @rate_limit
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            username = email.split('@')[0]  # Extract the part before '@'
            user, created = User.objects.get_or_create(username=username, email=email)
            
            # Generate and store OTP in cache
            otp = generate_otp()
            cache.set(f'otp_{user.id}', otp, timeout=300)  # OTP valid for 5 minutes
            
            send_mail(
                subject='Your OTP Code from Free Daily Horoscope',
                message=f'Free Daily Horoscope',
                from_email='Free Daily Horoscope <your_default_email@example.com>',
                recipient_list=[email],
                fail_silently=False,
                html_message=f'''
                                <html>
                                <body style="font-family: Arial, sans-serif; padding: 20px;">
                                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                                        <h2 style="color: #4CAF50;">Free Daily Horoscope</h2>
                                        <p style="font-size: 16px;">Your OTP code is <strong>{otp}</strong></p>
                                        <p style="font-size: 16px;">Use this code to login to Free Daily Horoscope.</p>
                                        <p style="font-size: 16px;">Do not share this code with anyone.</p>
                                        <p style="font-size: 16px;">Thank you,</p>
                                        <p style="font-size: 16px;"><strong>Free Daily Horoscope Team</strong></p>
                                    </div>
                                </body>
                                </html>
                            ''',
            )
            return Response({'message': 'OTP sent to email'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                stored_otp = cache.get(f'otp_{user.id}')
                
                if stored_otp is None:
                    return Response({'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
                
                if str(stored_otp) == str(otp):
                    # Clear the OTP from cache and login user
                    cache.delete(f'otp_{user.id}')
                    login(request, user)
                    return Response({'message': 'Login successful, new session started'}, status=status.HTTP_200_OK)
                
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResendOTPView(APIView):
    @rate_limit
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Generate and store OTP in cache
                otp = generate_otp()
                cache.set(f'otp_{user.id}', otp, timeout=300)  # OTP valid for 5 minutes
                
                send_mail(
                    subject='Your OTP Code from Free Daily Horoscope',
                    message=f'Free Daily Horoscope',
                    from_email='Free Daily Horoscope <your_default_email@example.com>',
                    recipient_list=[email],
                    fail_silently=False,
                    html_message=f'''
                                    <html>
                                    <body style="font-family: Arial, sans-serif; padding: 20px;">
                                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                                            <h2 style="color: #4CAF50;">Free Daily Horoscope</h2>
                                            <p style="font-size: 16px;">Your OTP code is <strong>{otp}</strong></p>
                                            <p style="font-size: 16px;">Use this code to login to Free Daily Horoscope.</p>
                                            <p style="font-size: 16px;">Do not share this code with anyone.</p>
                                            <p style="font-size: 16px;">Thank you,</p>
                                            <p style="font-size: 16px;"><strong>Free Daily Horoscope Team</strong></p>
                                        </div>
                                    </body>
                                    </html>
                                ''',
                )
                return Response({'message': 'OTP sent to email'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        return Response({'message': 'User is not authenticated'}, status=status.HTTP_400_BAD_REQUEST)
