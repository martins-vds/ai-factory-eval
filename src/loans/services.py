import csv
from io import StringIO

from django.db import transaction
from django.utils import timezone

from .models import Loan
from .repository import LoanRepository


@transaction.atomic
def lend_loan(member, isbn):
    return LoanRepository().create(
        id=f'L{Loan.objects.count() + 1}',
        member=member,
        isbn=isbn,
        lent_on=timezone.localdate(),
    )


@transaction.atomic
def return_loan(loan_id):
    loan = LoanRepository().find_for_update(loan_id)
    if loan is None:
        return None, False
    if loan.returned_on is not None:
        return loan, False

    loan.returned_on = timezone.localdate()
    loan.save(update_fields=['returned_on'])
    return loan, True


def loan_line(loan):
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    writer.writerow(
        [
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return output.getvalue()


def list_loans_text():
    return ''.join(loan_line(loan) for loan in LoanRepository().all())


def get_loan_text(loan_id):
    loan = LoanRepository().find(loan_id)
    return loan_line(loan) if loan else None
