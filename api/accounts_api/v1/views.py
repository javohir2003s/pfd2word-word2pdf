from django.conf import settings
import datetime
import jwt
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import UserProfile
from .permissions import IsAdminOrIsOwner
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserRegisterSerializer, VerifyOTPSerializer, LoginSerializer,
    ResendOTPSerializer, ProfileSerializer
)
from django.shortcuts import get_object_or_404


class UserRegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={"user": serializer.data}, status=status.HTTP_201_CREATED)


class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(data={"user": serializer.data}, status=status.HTTP_200_OK)


class ResendOTPAPIView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={"user": serializer.data}, status=status.HTTP_200_OK)


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh_token = serializer.validated_data['refresh_token']
        access_token = serializer.validated_data['access_token']
        return Response(
            data={
                "user": user,
                "refresh_token": refresh_token,
                "access_token": access_token,
            },
            status=status.HTTP_200_OK
        )


class RefreshTokenAPIView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response(
                {"error": "Refresh token talab qilinadi"}, status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'], options={"verify_signature": False})
            user_id = payload['user_id']

            access_payload = {
                "user_id": user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            }

            access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
            return Response({'access': access_token})

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Refresh token eskirgan'}, status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Xato Refresh token'}, status.HTTP_401_UNAUTHORIZED)


class ProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

