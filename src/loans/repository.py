from django.db import transaction

from src.loans.models import Loan


def all_loans():
    return Loan.objects.order_by('id')


def find_loan(loan_id):
    return Loan.objects.filter(pk=loan_id).first()


@transaction.atomic
def create_loan(*, loan_id, member, isbn, lent_on, returned_on=None):
    return Loan.objects.create(
        id=loan_id,
        member=member,
        isbn=isbn,
        lent_on=lent_on,
        returned_on=returned_on,
    )
