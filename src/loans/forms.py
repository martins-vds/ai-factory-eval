from django import forms


class LoanLendForm(forms.Form):
    member = forms.CharField(max_length=255, strip=False)
    isbn = forms.CharField(max_length=255, strip=False)
