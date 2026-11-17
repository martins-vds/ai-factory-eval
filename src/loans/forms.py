from django import forms


class LoanForm(forms.Form):
    member = forms.CharField(
        max_length=255,
        strip=False,
        error_messages={'required': 'Member is required.'},
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
    isbn = forms.CharField(
        max_length=255,
        strip=False,
        error_messages={'required': 'ISBN is required.'},
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )

    def clean_member(self):
        member = self.cleaned_data['member']
        if not member.strip():
            raise forms.ValidationError('Member is required.')
        return member

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if not isbn.strip():
            raise forms.ValidationError('ISBN is required.')
        return isbn
