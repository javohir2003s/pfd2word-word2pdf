from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet
from .views import (
    UserRegisterAPIView, VerifyOTPAPIView, ResendOTPAPIView,
    LoginAPIView, RefreshTokenAPIView, ProfileViewSet
)

router = DefaultRouter()
router.register(r'userme', ProfileViewSet, basename='profile')

urlpatterns = [
    path("register", UserRegisterAPIView.as_view(), name="user-register"),
    path("verify-phone", VerifyOTPAPIView.as_view(), name="verify-phone"),
    path('resend-code', ResendOTPAPIView.as_view(), name="resend-otp"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("refresh-token", RefreshTokenAPIView.as_view(), name="refresh-token"),
]

urlpatterns += router.urls