import os
from django.core.exceptions import ValidationError
import datetime
from uuid import uuid4

def generate_uploaded_file_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    today = datetime.datetime.today()
    date_folder = today.strftime("%Y-%m/%d")

    if ext == 'pdf':
        folder_type = "pdf"
    else:
        folder_type = "word"
    new_filename = f"{instance.user.profile.full_name}_{uuid4().hex}.{ext}"

    return os.path.join('uploaded_files', folder_type, date_folder, new_filename)

def generate_converted_file_path(filename, ext):
    today = datetime.datetime.today()
    date_folder = today.strftime("%Y-%m/%d")

    if ext == 'pdf':
        folder_type = "word"
        converted_ext = 'docx'
    else:
        folder_type = "pdf"
        converted_ext = 'pdf'

    return os.path.join('converted_files', folder_type, date_folder, f"{filename}.{converted_ext}")

def validate_file_size(value):
    max_file_size = 5
    if value.size > max_file_size * 1024 * 1024:
        raise ValidationError(f"Fayl hajmi {max_file_size}MB dan oshmasligi kerak")

def validate_file_extensions(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".pdf", ".doc", ".docx"]
    if ext.lower() not in valid_extensions:
        raise ValidationError("Faqat pdf yoki word fayllarga ruxsat beriladi")
