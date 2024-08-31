# scanner_app/serializers.py
from rest_framework import serializers

class ScanResultSerializer(serializers.Serializer):
    image_urls = serializers.ListField(child=serializers.URLField())
