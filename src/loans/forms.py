from django import forms


class LoanForm(forms.Form):
    member = forms.CharField(
        required=False,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered'}),
    )
    isbn = forms.CharField(
        required=False,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered'}),
    )
