from django import forms
from django.conf import settings


class VideoUploadForm(forms.Form):
    video = forms.FileField(label='MP4 video',widget=forms.ClearableFileInput(attrs={'accept':'.mp4,video/mp4'}),
        help_text='Up to 4 minutes and 200 MB (200,000,000 bytes). Both limits are checked by the server.')

    def clean_video(self):
        upload=self.cleaned_data['video']
        if not upload.name.lower().endswith('.mp4'):
            raise forms.ValidationError('Choose an MP4 file. Its actual media structure will also be checked.')
        if upload.size>settings.VIDEO_MAX_BYTES:
            raise forms.ValidationError('The upload exceeds 200 MB.')
        return upload
