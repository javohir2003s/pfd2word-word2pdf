from django.urls import path
from .views import api_root

urlpatterns = [
    path("home", api_root, name="api-root"),
]