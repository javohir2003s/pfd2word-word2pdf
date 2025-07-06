from django.urls import path
from .views import api_root

urlpatterns = [
    path("document", api_root, name="api-root"),
]