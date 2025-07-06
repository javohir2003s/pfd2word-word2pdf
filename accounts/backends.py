from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class PhoneNumberBackend(ModelBackend):
    def authenticate(self, request, phone_number=None, password=None, **kwargs):

        if phone_number is None or password is None:
            return None
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
