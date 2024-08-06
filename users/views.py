from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import OTP
from .serializers import UserSerializer, OTPSerializer
from django.contrib.auth import authenticate, login
from django.utils import timezone

class RegisterOrLoginView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user, created = User.objects.get_or_create(username=email, email=email)
            
            # Delete any existing OTPs
            OTP.objects.filter(user_id=user.id).delete()
            
            # Create and send new OTP
            otp_instance = OTP.objects.create(user_id=user.id)
            otp_instance.generate_otp()
            # send_mail(
            #     'Your OTP Code',
            #     f'Your OTP code is {otp_instance.otp}',
            #     'no-reply@example.com',
            #     [email],
            #     fail_silently=False,
            # )
            return Response({'message': 'OTP sent to email', "otp": otp_instance.otp}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                otp_instance = OTP.objects.filter(user=user).latest('created_at')
                
                if otp_instance.is_expired():
                    return Response({'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
                
                if otp_instance.otp == otp:
                    # Delete OTP and login user
                    otp_instance.delete()
                    login(request, user)
                    return Response({'message': 'Login successful, new session started'}, status=status.HTTP_200_OK)
                
                return Response({'message': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            except (User.DoesNotExist, OTP.DoesNotExist):
                return Response({'message': 'User or OTP not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResendOTPView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                OTP.objects.filter(user=user).delete()
                otp_instance = OTP.objects.create(user=user)
                otp_instance.generate_otp()
                # send_mail(
                #     'Your OTP Code',
                #     f'Your OTP code is {otp_instance.otp}',
                #     ' [email], 
                #     fail_silently=False,
                # )
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