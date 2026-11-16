from django import forms


class LoanForm(forms.Form):
    member = forms.CharField(max_length=255)
    isbn = forms.CharField(max_length=255)
