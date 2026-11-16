from django import forms


class LoanForm(forms.Form):
    member = forms.CharField(max_length=255, strip=False)
    isbn = forms.CharField(max_length=255, strip=False)

    def clean(self):
        cleaned_data = super().clean()
        for field in ('member', 'isbn'):
            value = cleaned_data.get(field)
            if value is not None and not value.strip():
                self.add_error(field, 'This field is required.')
        return cleaned_data
