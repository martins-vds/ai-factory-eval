from django import forms


class LoanLendForm(forms.Form):
    member = forms.CharField(max_length=255, strip=False)
    isbn = forms.CharField(max_length=255, strip=False)

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
