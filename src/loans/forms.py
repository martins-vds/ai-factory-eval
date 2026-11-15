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

    def clean_member(self):
        member = self.cleaned_data['member']
        if not member.strip():
            raise forms.ValidationError('This field is required.', code='required')
        return member

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if not isbn.strip():
            raise forms.ValidationError('This field is required.', code='required')
        return isbn
