from django import forms


class LoanForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
    isbn = forms.CharField(
        label='ISBN',
        max_length=255,
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        for field in self.fields:
            value = cleaned_data.get(field)
            if value is not None and not value.strip():
                self.add_error(
                    field,
                    forms.ValidationError('This field is required.', code='required'),
                )
        return cleaned_data
