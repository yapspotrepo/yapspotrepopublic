import os
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
#from healthdata.models import File
import magic

def validate_file_extension(value):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
    valid_mimes = ['image/jpeg', 'image/png', 'image/bmp', 'image/gif', 'image/tiff', 'image/webp']

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    mime_type = magic.from_buffer(value.read(1024), mime=True).lower()

    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension: ' + ext)

    if not mime_type in valid_mimes:
    	raise ValidationError(u'Unsupported file type: ' + mime_type)

    if value.size > 5242880:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")


def validate_image_file_extension(value):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
    valid_mimes = ['image/jpeg', 'image/png', 'image/bmp', 'image/gif', 'image/tiff', 'image/webp']

    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    mime_type = magic.from_buffer(value.read(1024), mime=True).lower()

    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Only image files accepted.  Unsupported file extension: ' + ext)

    if not mime_type in valid_mimes:
    	raise ValidationError(u'Only image files accepted.  Unsupported file type: ' + mime_type)

    if value.size > 5242880:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")