from django import forms
from .models import Poll
from .poll_services import validate_content


class GenerationForm(forms.Form):
    kind = forms.ChoiceField(choices=Poll.Kind.choices, label='Poll type')
    language = forms.ChoiceField(choices=Poll.Language.choices, label='Output language',initial='en')
    material = forms.CharField(max_length=6000, strip=False, widget=forms.Textarea(attrs={'rows':7, 'dir':'auto'}),
        label='Learning material', help_text='1–6000 Unicode characters, including whitespace. No files.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].widget.attrs.pop('maxlength', None)

    def clean_material(self):
        text = self.cleaned_data['material']
        if not text.strip():
            raise forms.ValidationError('Enter learning material, not whitespace only.')
        return text

    def clean_language(self):
        language=self.cleaned_data['language']
        if language=='he':
            raise forms.ValidationError('Automatic draft generation is currently available in English only. Hebrew polls can still be edited, published and answered.')
        return language


class DraftForm(forms.Form):
    version = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    question = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'dir':'auto'}))
    option_0 = forms.CharField(label='Option 1')
    option_1 = forms.CharField(label='Option 2')
    option_2 = forms.CharField(label='Option 3')
    option_3 = forms.CharField(label='Option 4')
    correct_index = forms.TypedChoiceField(choices=[(i, str(i+1)) for i in range(4)], coerce=int, label='Correct option')
    explanation = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'dir':'auto'}))

    def __init__(self, *args, poll, **kwargs):
        self.poll = poll
        initial = {'version':poll.version, 'question':poll.question, 'explanation':poll.explanation,
            'correct_index':poll.correct_index, **{f'option_{i}':v for i,v in enumerate(poll.options)}}
        super().__init__(*args, initial=initial, **kwargs)
        if poll.kind == Poll.Kind.OPINION:
            del self.fields['correct_index']
            del self.fields['explanation']
        for name in self.fields:
            if name.startswith('option_'):
                self.fields[name].widget.attrs['dir'] = 'auto'

    def clean(self):
        cleaned = super().clean()
        # Reject forged answer metadata on opinion drafts rather than ignoring it.
        if self.poll.kind == Poll.Kind.OPINION and any(key in self.data for key in ['correct_index','explanation']):
            raise forms.ValidationError('Opinion polls cannot have a correct answer or explanation.')
        if not self.errors:
            validate_content(self.poll.kind, self.content())
        return cleaned

    def content(self):
        data = {'question':self.cleaned_data['question'], 'options':[self.cleaned_data[f'option_{i}'] for i in range(4)]}
        if self.poll.kind == Poll.Kind.COMPREHENSION:
            data.update(correct_index=self.cleaned_data['correct_index'], explanation=self.cleaned_data['explanation'])
        return data


class VoteForm(forms.Form):
    option_index = forms.TypedChoiceField(coerce=int, widget=forms.RadioSelect(attrs={'class':'poll-choice-input'}), choices=[])

    def __init__(self, *args, poll, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['option_index'].choices = list(enumerate(poll.options))


class VersionForm(forms.Form):
    version = forms.IntegerField(min_value=1)
