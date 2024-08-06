from django.urls import path
from .views import RegisterOrLoginView, VerifyOTPView, ResendOTPView, LogoutView

urlpatterns = [
    path('register-or-login/', RegisterOrLoginView.as_view(), name='register_or_login'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
