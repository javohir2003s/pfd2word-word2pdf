from django.urls import path
from .views import FileUploadListAPIView, FileDetailAPIView

urlpatterns = [
    path("files", FileUploadListAPIView.as_view(), name="files"),
    path("files/<int:pk>", FileDetailAPIView.as_view(), name="files"),
]