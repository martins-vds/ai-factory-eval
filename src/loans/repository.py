from django.db import transaction

from src.loans.models import Loan


def all_loans():
    return Loan.objects.all()


def find_loan(loan_id):
    return Loan.objects.filter(pk=loan_id).first()


@transaction.atomic
def save_loan(loan):
    loan.save()
    return loan
