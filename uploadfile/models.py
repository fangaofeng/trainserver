from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
# Create your models here.


class uploadfile(models.Model):

    file = models.FileField(upload_to='./uploadfile/', blank=True)
    FILE_TYPE_CHOICES = (
        ('PDF', 'PDF'),
        ('MP4', 'MP4'),
        ('JPG', 'JPG'),
        ('PNG', 'PNG'),
        ('TXT', 'TXT'),
        ('NO', 'NO'),
    )
    type = models.CharField(
        max_length=3,
        choices=FILE_TYPE_CHOICES,
        default='NO',
    )

    class Meta:
        verbose_name = _('upload file')
        verbose_name_plural = _('upload_file')

    def __str__(self):
        return str(self.id)
