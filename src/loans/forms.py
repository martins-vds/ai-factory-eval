from django import forms


def validate_not_blank(value):
    if not value.strip():
        raise forms.ValidationError('This field is required.')


class LoanForm(forms.Form):
    member = forms.CharField(
        strip=False,
        validators=[validate_not_blank],
        widget=forms.TextInput(
            attrs={'class': 'input input-bordered w-full', 'autocomplete': 'name'}
        ),
    )
    isbn = forms.CharField(
        strip=False,
        validators=[validate_not_blank],
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
