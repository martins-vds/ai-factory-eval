from django import forms


class LendLoanForm(forms.Form):
    member = forms.CharField(max_length=255, required=False, strip=False)
    isbn = forms.CharField(max_length=255, required=False, strip=False)

    def clean_member(self):
        member = self.cleaned_data['member']
        if not member.strip():
            raise forms.ValidationError('Enter a member name; blank values are not accepted.')
        return member

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']
        if not isbn.strip():
            raise forms.ValidationError('Enter an ISBN; blank values are not accepted.')
        return isbn
