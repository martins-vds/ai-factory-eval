from django import forms


class LoanForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered'}),
    )
    isbn = forms.CharField(
        max_length=255,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered'}),
    )
