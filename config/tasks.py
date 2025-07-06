from celery import shared_task
from config import settings
from documents.models import FileConverter
import os
from pdf2docx import Converter
import subprocess
from documents.utils import generate_converted_file_path


@shared_task
def convert_single_file(file_id):
    try:
        file_obj = FileConverter.objects.get(pk=file_id)
        uploaded_file_path = file_obj.uploaded_file.path
        filename, ext = os.path.splitext(os.path.basename(uploaded_file_path))
        ext = ext.lstrip(".")
        print(ext)

        if ext.lower() == "pdf":
            relative_converted_file_path = generate_converted_file_path(filename, ext) #converted_files/word/2025/07/5/filename.word
            absolute_converted_file_path = os.path.join(settings.MEDIA_ROOT, relative_converted_file_path) #home/javohir/Projects/file_generate/media/converted_files/word/2025/07/5/filename.word

            output_dir = os.path.dirname(absolute_converted_file_path) #home/javohir/Projects/file_generate/media/converted_files/word/2025/07/5/
            if not os.path.exists(output_dir):
                os.makedirs(output_dir) #shu papkani yaratadi

            cv = Converter(uploaded_file_path)
            cv.convert(absolute_converted_file_path)
            cv.close()

            file_obj.converted_file.name = relative_converted_file_path

        elif ext.lower() in ("docx", "doc"):
            relative_converted_file_path = generate_converted_file_path(filename, ext) #converted_files/pdf/2025/07/5/filename.
            absolute_converted_file_path = os.path.join(settings.MEDIA_ROOT, relative_converted_file_path)
            output_dir = os.path.dirname(absolute_converted_file_path)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir) #
            try:
                subprocess.run([
                    "libreoffice", "--headless", "--convert-to", "pdf",
                    "--outdir", output_dir,
                    uploaded_file_path
                ], check=True)
            except subprocess.CalledProcessError as e:
                print("LibreOffice error:", e)
                raise

            file_obj.converted_file.name = relative_converted_file_path

        file_obj.is_celery_checked = True
        file_obj.save()

    except Exception as e:
        print(f"Error converting file {file_id}: {e}")

@shared_task
def convert_files():
    unconverted_files = FileConverter.objects.filter(is_celery_checked=False).order_by('uploaded_at')[:100]
    print(f"Found {len(unconverted_files)} unconverted files")

    for file_obj in unconverted_files:
        convert_single_file.delay(file_obj.id)


