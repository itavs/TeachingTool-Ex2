"""Assignment metadata and exact-text submission forms; no AI calls."""
from django import forms


class AssignmentForm(forms.Form):
    title = forms.CharField(max_length=160)
    instructions = forms.CharField(strip=False, widget=forms.Textarea(attrs={"rows": 6, "dir": "auto"}))
    criteria = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "dir": "auto"}),
                               help_text="Enter one review criterion per line.")

    def clean_instructions(self):
        text = self.cleaned_data["instructions"]
        if not text.strip():
            raise forms.ValidationError("Enter assignment instructions.")
        return text

    def clean_criteria(self):
        criteria = [line.strip() for line in self.cleaned_data["criteria"].splitlines() if line.strip()]
        if not criteria:
            raise forms.ValidationError("Enter at least one review criterion.")
        return criteria


class SubmissionForm(forms.Form):
    text = forms.CharField(strip=False, label="Your work",
                           widget=forms.Textarea(attrs={"rows": 14, "dir": "auto"}),
                           help_text="Each submission saves a new version. Previous versions are kept.")

    def clean_text(self):
        text = self.cleaned_data["text"]
        if not text.strip():
            raise forms.ValidationError("Paste your work before submitting.")
        return text
