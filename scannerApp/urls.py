from django.urls import path
from .views import home, upload_document, ScanDocumentAPIView, UploadDocumentAPIView, preview_images, save_document

urlpatterns = [
    path('', home, name='home'),
    path('upload/', upload_document, name='upload-document'),
    path('scan/', ScanDocumentAPIView.as_view(), name='scan-document'),
    path('upload-doc/', UploadDocumentAPIView.as_view(), name='upload-doc'),
    path('save/', save_document, name='save-document'),
    path('preview/', preview_images, name='preview-images'),
]
