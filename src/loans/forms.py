from django import forms


class LoanForm(forms.Form):
    member = forms.CharField(
        strip=False,
        widget=forms.TextInput(
            attrs={'class': 'input input-bordered w-full', 'autocomplete': 'name'}
        ),
    )
    isbn = forms.CharField(
        strip=False,
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )

    def clean_member(self):
        member = self.cleaned_data['member']
        if not member.strip():
            raise forms.ValidationError('This field is required.')
        return member

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if not isbn.strip():
            raise forms.ValidationError('This field is required.')
        return isbn
