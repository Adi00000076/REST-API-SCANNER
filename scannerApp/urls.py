from django.urls import path
from .views import scan_document

urlpatterns = [
    path('api/scan/', scan_document, name='scan_document'),
]
