

from django.db import models

class ScannedImage(models.Model):
    file = models.FileField(upload_to='scanned_images/')
    color_mode = models.CharField(max_length=20)
    zoom_level = models.IntegerField()
    page_number = models.IntegerField()

    def __str__(self):
        return self.file.name
