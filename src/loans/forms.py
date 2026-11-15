from django import forms


class LoanForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
    isbn = forms.CharField(
        max_length=255,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )

    def clean_member(self):
        value = self.cleaned_data['member']
        if not value.strip():
            raise forms.ValidationError('This field is required.')
        return value

    def clean_isbn(self):
        value = self.cleaned_data['isbn']
        if not value.strip():
            raise forms.ValidationError('This field is required.')
        return value
