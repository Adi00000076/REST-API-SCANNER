# admin.py

from django.contrib import admin
from .models import ScannedImage

@admin.register(ScannedImage)
class ScannedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'color_mode', 'zoom_level', 'page_number', 'file')
    search_fields = ('color_mode', 'zoom_level', 'page_number')
    list_filter = ('color_mode', 'zoom_level')
    readonly_fields = ('file',)
