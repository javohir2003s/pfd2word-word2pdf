from django.db import models
from django.contrib.auth import get_user_model
from .utils import (
    generate_converted_file_path, generate_uploaded_file_path,
    validate_file_size, validate_file_extensions
)


User = get_user_model()

class FileConverter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_file = models.FileField(
        upload_to=generate_uploaded_file_path,
        validators=[validate_file_size, validate_file_extensions],
        max_length=255
    )
    converted_file = models.FileField(
        upload_to=generate_converted_file_path,
        max_length=255,
        null=True, blank=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_celery_checked = models.BooleanField(default=False)

    def __str__(self):
        return self.user.profile.full_name