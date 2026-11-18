from django import forms

from .models import Loan


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ('member', 'isbn')
        widgets = {
            'member': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'isbn': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
        }
