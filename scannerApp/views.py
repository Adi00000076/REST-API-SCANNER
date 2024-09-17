import os
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import win32com.client
import pythoncom
import logging
from PIL import Image
import io
import time
from django.shortcuts import render

logger = logging.getLogger(__name__)

# Mapping color modes to their respective values
COLOR_MODE_VALUES = {
    'Color': 1,
    'Grayscale': 2,
    'Halftone': 3,
    'Black/White': 4,
    'Auto Detect Color': 5
}

# Page sizes in inches (Width x Height)
PAGE_SIZE_DIMENSIONS = {
    'Legal': (8.5, 14),               # 8.5x14 inches
    'A4': (8.27, 11.69),             # 210x297 mm
    '3.5x5in': (3.5, 5),             # 3.5x5 inches
    '4x6in': (4, 6),                 # 4x6 inches
    '5x7in': (5, 7),                 # 5x7 inches
    '8x10in': (8, 10),               # 8x10 inches
    'Plastic Card': (3.375, 2.125),  # 3.375x2.125 inches
    'Business Card': (3.5, 2),        # 3.5x2 inches
    'Letter': (8.5, 14)
}

# Supported resolution (PPI) values
RESOLUTION_VALUES = [75, 150, 200, 240, 300, 400, 500, 600]

# Page orientations
PAGE_ORIENTATIONS = {
    'Detect Orientation': 0,
    'Portrait': 1,
    'Landscape': 2
}

@api_view(['POST'])
def scan_document(request):
    """
    API to scan a document and adjust image properties.
    Parameters:
    - color_mode (str): Color mode for scanning. // Color mode for scanning (Options: Color, Grayscale, Halftone, Black/White, Auto Detect Color)
    - page_size (str): Page size for scanning. // Page size for scanning (Options: Legal, A4, 3.5x5in, 4x6in, 5x7in, 8x10in, Plastic Card, Business Card)
    - page_orientation (str): Page orientation for scanning. // Page orientation for scanning (Options: Detect Orientation, Portrait, Landscape)
    - auto_scan (bool): Automatically determine number of pages to scan. // Automatically determine the number of pages to scan
    - dpi (int): DPI (dots per inch) setting for scanning. // DPI (dots per inch) setting for scanning
    - resolution (int): Resolution (PPI) setting. // Resolution (PPI) setting for scanning
    - file_format (str): File format for saving the image (JPEG, PNG). // File format for saving the image (Options: JPEG, PNG)
    """
    try:
        # Log the received parameters
        logger.info(f"Received request data: {request.data}")

        # Default parameter values
        color_mode = request.data.get('color_mode', 'Color')
        page_size = request.data.get('page_size', 'A4')
        page_orientation = request.data.get('page_orientation', 'Portrait')
        auto_scan = request.data.get('auto_scan', False)
        dpi = int(request.data.get('dpi', 150))
        resolution = int(request.data.get('resolution', 150))

        # Validate color_mode
        if color_mode not in COLOR_MODE_VALUES:
            logger.error(f"Invalid color_mode: {color_mode}")
            return Response({"error": "Invalid color_mode value. Options: Color, Grayscale, Halftone, Black/White, Auto Detect Color."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate page_size
        if page_size not in PAGE_SIZE_DIMENSIONS:
            logger.error(f"Invalid page_size: {page_size}")
            return Response({"error": "Invalid page_size value. Options: Legal, A4, 3.5x5in, 4x6in, 5x7in, 8x10in, Plastic Card, Business Card."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate page_orientation
        if page_orientation not in PAGE_ORIENTATIONS:
            logger.error(f"Invalid page_orientation: {page_orientation}")
            return Response({"error": "Invalid page_orientation value. Options: Detect Orientation, Portrait, Landscape."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate resolution
        if resolution not in RESOLUTION_VALUES:
            logger.error(f"Invalid resolution: {resolution}")
            return Response({"error": "Invalid resolution value. Options: 75, 150, 200, 240, 300, 400, 500, 600."}, status=status.HTTP_400_BAD_REQUEST)

        pythoncom.CoInitialize()
        wia = win32com.client.Dispatch("WIA.CommonDialog")
        logger.info("WIA CommonDialog dispatched successfully.")

        device_manager = win32com.client.Dispatch("WIA.DeviceManager")
        logger.info("WIA DeviceManager dispatched successfully.")

        devices = device_manager.DeviceInfos
        logger.info(f"Number of devices found: {devices.Count}")

        if devices.Count == 0:
            logger.error("No scanner devices found.")
            return Response({"error": "No scanner devices found."}, status=status.HTTP_400_BAD_REQUEST)

        default_device = devices.Item(1).Connect()
        scan_item = default_device.Items[1]

        scanned_files = []

        page = 0
        while True:
            retry_attempts = 3
            success = False
            for attempt in range(retry_attempts):
                try:
                    color_mode_value = COLOR_MODE_VALUES[color_mode]
                    scan_item.Properties("6146").Value = color_mode_value

                    effective_dpi = int(dpi)
                    scan_item.Properties("6147").Value = effective_dpi  # Horizontal DPI
                    scan_item.Properties("6148").Value = effective_dpi  # Vertical DPI

                    # Set page size and orientation if supported
                    # Add additional settings as per your scanner's API
                    # scan_item.Properties("YourPageSizeProperty").Value = PAGE_SIZE_DIMENSIONS[page_size]
                    # scan_item.Properties("YourOrientationProperty").Value = PAGE_ORIENTATIONS[page_orientation]

                    image = scan_item.Transfer()

                    # Choose file format based on request, default to JPEG
                    file_format = request.data.get('file_format', 'JPEG').upper()
                    if file_format not in ['JPEG', 'PNG']:
                        file_format = 'JPEG'

                    # Save the image to a temporary file
                    unique_filename = f"scanned_image_{page+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_format.lower()}"
                    temp_file_path = os.path.join(settings.MEDIA_ROOT, unique_filename)

                    # Convert the WIA image to PIL Image and save it
                    image_data = image.FileData.BinaryData
                    pil_image = Image.open(io.BytesIO(image_data))

                    # Save the image with the specified format
                    if file_format == 'JPEG':
                        pil_image.save(temp_file_path, 'JPEG', resolution=resolution)
                    else:
                        pil_image.save(temp_file_path, file_format, optimize=True)

                    # Check and ensure the file size is in KB range
                    file_size = os.path.getsize(temp_file_path) / 1024  # Size in KB
                    if file_size > 1024:  # If larger than 1MB, reduce quality further
                        for q in range(85, 10, -10):
                            if file_format == 'JPEG':
                                pil_image.save(temp_file_path, 'JPEG', resolution=resolution)
                            else:
                                pil_image.save(temp_file_path, file_format, optimize=True, quality=q)
                            file_size = os.path.getsize(temp_file_path) / 1024
                            if file_size <= 1024:
                                break

                    logger.info(f"Scanned image page {page+1} saved to {temp_file_path} with size {file_size:.2f} KB")

                    scanned_files.append(settings.MEDIA_URL + unique_filename)
                    success = True
                    break  # Exit retry loop on success

                except Exception as scan_error:
                    logger.error(f"Error scanning page {page+1} (attempt {attempt+1}): {scan_error}")
                    time.sleep(2)  # Wait before retrying

            if not success or not auto_scan:
                break  # Exit if scan failed or auto_scan is False

            page += 1

        return Response({"image_urls": scanned_files})

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    finally:
        pythoncom.CoUninitialize()
        logger.info("COM library uninitialized")

def home(request):
    return render(request, 'home.html')
