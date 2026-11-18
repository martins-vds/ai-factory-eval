from django import forms

from .services import lending_errors


class LoanForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        error_messages={'required': 'Member is required.'},
        strip=False,
    )
    isbn = forms.CharField(
        max_length=255,
        error_messages={'required': 'ISBN is required.'},
        strip=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        errors = lending_errors(
            cleaned_data.get('member'),
            cleaned_data.get('isbn'),
        )
        for field, message in errors.items():
            if field in cleaned_data:
                self.add_error(field, message)
        return cleaned_data
