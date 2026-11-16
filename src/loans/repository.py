from django.db import transaction

from src.loans.models import Loan


def list_loans():
    return Loan.objects.order_by('pk')


@transaction.atomic
def save_loan(loan):
    loan.save()
    return loan
