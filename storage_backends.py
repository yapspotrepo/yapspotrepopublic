from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import os
from tempfile import SpooledTemporaryFile
from PIL import Image, ExifTags
from io import BytesIO

class StaticStorage(S3Boto3Storage):

    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = settings.AWS_STORAGE_BUCKET_NAME_STATIC
        kwargs['location'] = settings.AWS_STATIC_LOCATION
        kwargs['default_acl'] = 'public-read'
        kwargs['file_overwrite'] = False
        kwargs['querystring_auth'] = False
        super(StaticStorage, self).__init__(*args, **kwargs)




class PrivateMediaStorage(S3Boto3Storage):

    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = settings.AWS_STORAGE_BUCKET_NAME_MEDIA
        kwargs['location'] = settings.AWS_PRIVATE_MEDIA_LOCATION
        kwargs['default_acl'] = 'private'
        kwargs['file_overwrite'] = False
        kwargs['custom_domain'] = False
        super(PrivateMediaStorage, self).__init__(*args, **kwargs)

    def _save_content(self, obj, content, parameters):
        """
        We create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload where as the storage backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(PrivateMediaStorage, self)._save_content(obj, content_autoclose, parameters)
        
        # Cleanup if this is fixed upstream our duplicate should always close        
        if not content_autoclose.closed:
            content_autoclose.close()


