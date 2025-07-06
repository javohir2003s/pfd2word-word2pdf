from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from .serializers import FileUploadSerializer
from .permissions import IsAdminOrIsOwner
from documents.models import FileConverter


class FileUploadListAPIView(ListCreateAPIView):
    queryset = FileConverter.objects.all()
    permission_classes = (IsAuthenticated, IsAdminOrIsOwner)
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return FileConverter.objects.all()
        return FileConverter.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FileDetailAPIView(RetrieveAPIView):
    queryset = FileConverter.objects.all()
    serializer_class = FileUploadSerializer
    permission_classes = (IsAuthenticated, IsAdminOrIsOwner)

