from django import forms
from django.core.exceptions import ValidationError


class LoanForm(forms.Form):
    member = forms.CharField(
        strip=False,
        error_messages={'required': 'This field cannot be blank.'},
        widget=forms.TextInput(attrs={'class': 'input input-bordered'}),
    )
    isbn = forms.CharField(
        strip=False,
        error_messages={'required': 'This field cannot be blank.'},
        widget=forms.TextInput(attrs={'class': 'input input-bordered'}),
    )

    def clean_member(self):
        value = self.cleaned_data['member']
        if not value.strip():
            raise ValidationError('This field cannot be blank.')
        return value

    def clean_isbn(self):
        value = self.cleaned_data['isbn']
        if not value.strip():
            raise ValidationError('This field cannot be blank.')
        return value
