import uuid
from django import forms
from .models import MeetingRequest


class RequestForm(forms.Form):
    kind = forms.ChoiceField(choices=MeetingRequest.Kind.choices)
    text = forms.CharField(min_length=1, max_length=1000, strip=True,
        widget=forms.Textarea(attrs={"rows": 4}), help_text="1–1000 characters. Stored only after a successful submission.")
    submission_id = forms.UUIDField(initial=uuid.uuid4, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Browser maxlength counts UTF-16 units; validation here counts code points.
        self.fields["text"].widget.attrs.pop("maxlength", None)

    def clean_text(self):
        value = self.cleaned_data["text"]
        # Python Unicode code points are the server-side length definition.
        if not 1 <= len(value) <= 1000:
            raise forms.ValidationError("Enter between 1 and 1000 characters.")
        return value
