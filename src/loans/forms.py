from django import forms


class LendLoanForm(forms.Form):
    member = forms.CharField(
        label='Member',
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'input input-bordered w-full bg-[#fffdf7]'}
        ),
    )
    isbn = forms.CharField(
        label='ISBN',
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'input input-bordered w-full bg-[#fffdf7]'}
        ),
    )
