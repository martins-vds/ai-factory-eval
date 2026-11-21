from django import forms


class LendLoanForm(forms.Form):
    member = forms.CharField(max_length=255, strip=False)
    isbn = forms.CharField(max_length=255, strip=False)
