import csv
from io import StringIO

from django.utils import timezone

from .models import Loan
from .repository import LoanRepository


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


def lend_loan(member, isbn):
    return LoanRepository().create(
        id=f'L{Loan.objects.count() + 1}',
        member=member,
        isbn=isbn,
        lent_on=timezone.localdate(),
    )


def return_loan(loan_id):
    loan = LoanRepository().find(loan_id)
    if loan is None:
        return None, False
    updated = Loan.objects.filter(pk=loan_id, returned_on__isnull=True).update(
        returned_on=timezone.localdate()
    )
    loan.refresh_from_db()
    return loan, bool(updated)
