from rest_framework import serializers
from accounts.models import CustomUser, PhoneOTP, UserProfile
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import re
from django.contrib.auth import authenticate


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone_number", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_phone_number(self, value):
        if not value[1:].isdigit() or not value.startswith('+998') or len(value) != 13:
            raise serializers.ValidationError("Telefon raqamni to'g'ri formatda kiriting.")

        user = CustomUser.objects.filter(phone_number=value).first()
        if user:
            raise serializers.ValidationError("Bunday telefon raqam bilan ro'yxatdan o'tilgan.")

        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Parolda kamida bitta katta harf bo'lishi kerak.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Parolda kamida bitta kichik harf bo'lishi kerak.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Parolda kamida bitta raqam bo'lishi kerak.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            raise serializers.ValidationError("Parollar mos emas")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")

        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        phone_number = validated_data["phone_number"]
        password = validated_data["password"]
        user = CustomUser.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            is_active=False,
        )

        otp_code = PhoneOTP.generate_otp()
        print(otp_code)
        PhoneOTP.objects.create(phone_number=phone_number, otp=otp_code)

        return user


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(min_length=13, max_length=13)
    otp_code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        otp_code = attrs.get("otp_code")

        try:
            phone_otp = PhoneOTP.objects.get(phone_number=phone_number)
        except PhoneOTP.DoesNotExist:
            raise serializers.ValidationError("Bunday telefon raqam topilmadi.")

        if phone_otp.is_locked():
            raise serializers.ValidationError("Urinishlar soni oshib ketgan. Keyinroq urinib ko‘ring")

        if phone_otp.is_expired():
            raise serializers.ValidationError("Kodni amal qilish muddati tugagan")

        if phone_otp.otp != otp_code:
            phone_otp.increment_attempts()
            raise serializers.ValidationError("Kod noto‘g‘ri")

        attrs['otp_instance'] = phone_otp

        phone_otp.is_verified = True
        phone_otp.locked_until = None
        phone_otp.attempts = 0
        phone_otp.save()

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            user.is_active = True
            user.save()
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Foydalanuvchi topilmadi")

        return attrs


class ResendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(min_length=13, max_length=13)

    def validate_phone_number(self, value):
        try:
            phone_otp = PhoneOTP.objects.get(phone_number=value)
        except PhoneOTP.DoesNotExist:
            raise serializers.ValidationError("Bunday telefon raqam topilmadi.")

        if phone_otp.is_verified:
            raise serializers.ValidationError("Bu raqam allaqachon tasdiqlangan")

        if not phone_otp.can_resend():
            raise serializers.ValidationError("Kodni yuborishda xatolik iltimos keyinroq urinib ko'ring")

        self.instance = phone_otp
        return value

    def save(self, **kwargs):
        phone_otp = self.instance
        phone_otp.otp = PhoneOTP.generate_otp()
        phone_otp.created_at = timezone.now()
        phone_otp.save()


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(min_length=13, max_length=13)
    password = serializers.CharField(max_length=100)

    def validate_phone_number(self, value):
        if not value[1:].isdigit() or not value.startswith('+998') or len(value) != 13:
            raise serializers.ValidationError("Telefon raqamni to'g'ri formatda kiriting")

        user = CustomUser.objects.filter(phone_number=value).first()
        if not user:
            raise serializers.ValidationError("Telefon raqam noto'g'ri yoki ro'yxatdan o'tmagan")

        return value

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")
        request = self.context.get("request")

        user = authenticate(request=request, phone_number=phone_number, password=password)

        if user is None:
            raise serializers.ValidationError("Telefon raqam yoki parol noto‘g‘ri")

        if not user.is_active:
            raise serializers.ValidationError("Foydalanuvchi topilmadi")

        refresh_token = RefreshToken.for_user(user)
        return {
            "user": user.phone_number,
            "refresh_token": str(refresh_token),
            "access_token": str(refresh_token.access_token)
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'role']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'email', 'age', 'profile_img', 'birth_date', 'address', 'balance']
        read_only_fields = ['user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request", None)
        user = request.user if request else None

        if user and not user.is_staff:
            self.fields['balance'].read_only = True