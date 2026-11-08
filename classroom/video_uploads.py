from django.conf import settings
from django.core.files.uploadhandler import FileUploadHandler, StopUpload


class BoundedUploadHandler(FileUploadHandler):
    """Bound actual multipart bytes before temporary disk storage, not MIME claims."""
    def __init__(self, request=None):
        super().__init__(request)
        self.total = 0

    def receive_data_chunk(self, raw_data, start):
        self.total += len(raw_data)
        if self.total > settings.VIDEO_MAX_BYTES:
            self.request.video_upload_error = 'The upload exceeds 200 MB.'
            raise StopUpload(connection_reset=False)
        return raw_data

    def file_complete(self, file_size):
        return None
