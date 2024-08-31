from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import uuid
from datetime import datetime
import win32com.client
import pythoncom
import logging
from django.conf import settings
from PIL import Image, ImageEnhance
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

# View for uploading documents
@require_POST
def upload_document(request):
    files = request.FILES.getlist('files')
    uploaded_files = []

    for f in files:
        filename = f.name
        destination = open(os.path.join(settings.MEDIA_ROOT, filename), 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        uploaded_files.append(settings.MEDIA_URL + filename)

    return JsonResponse({'uploaded_files': uploaded_files})

# API view for scanning documents
class ScanDocumentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            pythoncom.CoInitialize()
            wia = win32com.client.Dispatch("WIA.CommonDialog")
            device_manager = win32com.client.Dispatch("WIA.DeviceManager")
            devices = device_manager.DeviceInfos
            
            if devices.Count == 0:
                return Response({"error": "No scanner devices found."}, status=status.HTTP_400_BAD_REQUEST)
            
            default_device = devices.Item(1).Connect()
            scan_item = default_device.Items[1]

            color_mode = request.data.get('color_mode', 'Color')
            zoom_level = int(request.data.get('zoom_level', 100))
            num_pages = int(request.data.get('num_pages', 1))

            scanned_files = []

            for page in range(num_pages):
                try:
                    scan_item.Properties("6146").Value = 2 if color_mode == 'Grayscale' else 1

                    dpi = int(300 * (zoom_level / 100))
                    scan_item.Properties("6147").Value = dpi
                    scan_item.Properties("6148").Value = dpi

                    image = scan_item.Transfer()

                    unique_filename = f"scanned_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}_page_{page+1}.jpg"
                    output_file = os.path.join(settings.MEDIA_ROOT, unique_filename)

                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    image.SaveFile(output_file)

                    scanned_files.append(settings.MEDIA_URL + unique_filename)

                except Exception as scan_error:
                    logger.error(f"Error scanning page {page+1}: {scan_error}")
                    break

            if not scanned_files:
                return Response({"error": "No images were scanned."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return redirect(reverse('preview-images') + f'?image_urls={"&image_urls=".join(scanned_files)}')

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            pythoncom.CoUninitialize()

# API view for uploading documents
class UploadDocumentAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            uploaded_files = request.FILES.getlist('files')
            uploaded_file_urls = []

            for file in uploaded_files:
                unique_filename = f"uploaded_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}_{file.name}"
                output_file = os.path.join(settings.MEDIA_ROOT, unique_filename)

                os.makedirs(os.path.dirname(output_file), exist_ok=True)

                with open(output_file, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                uploaded_file_urls.append(settings.MEDIA_URL + unique_filename)

            if not uploaded_file_urls:
                return Response({"error": "No files were uploaded."}, status=status.HTTP_400_BAD_REQUEST)

            return redirect(reverse('preview-images') + f'?image_urls={"&image_urls=".join(uploaded_file_urls)}')
        
        except Exception as e:
            logger.error(f"Unexpected error while uploading files: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View for saving documents
def save_document(request):
    if request.method == 'POST':
        file_name = request.POST.get('fileName')
        format = request.POST.get('format')
        pages = request.POST.get('pages')
        custom_info = request.POST.get('customInfo')

        # Implement the logic to save the document
        # ...

        return redirect('preview-images')  # Redirect to a relevant page after saving
    return render(request, 'scan/save_document.html')

# View for previewing images
def preview_images(request):
    image_urls = request.GET.getlist('image_urls')
    if not image_urls:
        image_urls = request.GET.get('image_urls', '').split('&image_urls=')
    logger.info(f"Previewing images: {image_urls}")
    return render(request, 'scan/preview.html', {'image_urls': image_urls})

# Home view
def home(request):
    return render(request, 'scan/home.html')

