from django.db import transaction

from src.loans.models import Loan


def list_loans():
    return Loan.objects.order_by('id')


def get_loan(loan_id):
    try:
        return Loan.objects.get(pk=loan_id)
    except Loan.DoesNotExist:
        return None


@transaction.atomic
def save_loan(loan):
    loan.save()
    return loan
