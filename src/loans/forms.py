from django import forms
from django.core.exceptions import ValidationError


class LoanLendForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        strip=False,
        error_messages={'required': 'Enter a member name; blank values are not accepted.'},
    )
    isbn = forms.CharField(
        max_length=255,
        strip=False,
        error_messages={'required': 'Enter an ISBN; blank values are not accepted.'},
    )

    def clean_member(self):
        member = self.cleaned_data['member']
        if not member.strip():
            raise ValidationError('Enter a member name; blank values are not accepted.')
        return member

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if not isbn.strip():
            raise ValidationError('Enter an ISBN; blank values are not accepted.')
        return isbn
