from datetime import date

from django.db import transaction

from src.loans.models import Loan


def list_loans():
    return Loan.objects.order_by('pk')


def find_loan(loan_id):
    return Loan.objects.filter(pk=loan_id).first()


@transaction.atomic
def create_loan(*, loan_id: str, member: str, isbn: str, lent_on: date) -> Loan:
    return Loan.objects.create(
        pk=loan_id,
        member=member,
        isbn=isbn,
        lent_on=lent_on,
    )
