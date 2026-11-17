from django import forms


class LendLoanForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
    isbn = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
