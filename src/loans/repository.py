from django.db import transaction

from .models import Loan


@transaction.atomic
def list_loans():
    return list(Loan.objects.order_by('id'))


@transaction.atomic
def get_loan(loan_id):
    return Loan.objects.filter(pk=loan_id).first()
