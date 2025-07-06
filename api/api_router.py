from django.urls import path, include

urlpatterns = [
    path('v1/accounts/', include('api.accounts_api.v1.urls')),
    path('v2/accounts/', include('api.accounts_api.v2.urls')),

    path('v1/documents/', include('api.documents_api.v1.urls')),
    path('v2/documents/', include('api.documents_api.v2.urls')),
]
