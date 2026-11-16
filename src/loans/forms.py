from django import forms
from django.core.exceptions import ValidationError


class LoanLendForm(forms.Form):
    member = forms.CharField(
        label='Member',
        max_length=255,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
        error_messages={'required': 'Enter a member.'},
    )
    isbn = forms.CharField(
        label='ISBN',
        max_length=255,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
        error_messages={'required': 'Enter an ISBN.'},
    )

    def clean_member(self):
        member = self.cleaned_data['member']
        if not member.strip():
            raise ValidationError('Enter a member.')
        return member

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if not isbn.strip():
            raise ValidationError('Enter an ISBN.')
        return isbn
