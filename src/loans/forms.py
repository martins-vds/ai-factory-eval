from django import forms


class LoanLendForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        error_messages={'required': 'Member name is required.'},
    )
    isbn = forms.CharField(
        max_length=255,
        error_messages={'required': 'ISBN is required.'},
    )
