from django import forms


class LoanLendingForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        strip=True,
        error_messages={'required': 'Enter a member name; blank values are not accepted.'},
    )
    isbn = forms.CharField(
        max_length=255,
        strip=True,
        error_messages={'required': 'Enter an ISBN; blank values are not accepted.'},
    )
