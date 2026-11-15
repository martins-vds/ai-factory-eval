import csv
from io import StringIO

from django.utils import timezone

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
    if loan_field_errors(member, isbn):
        return None

    return LoanRepository().lend(
        member=member,
        isbn=isbn,
        lent_on=timezone.localdate(),
    )


def loan_field_errors(member, isbn):
    errors = {}
    if not member or not member.strip():
        errors['member'] = 'Member is required.'
    if not isbn or not isbn.strip():
        errors['isbn'] = 'ISBN is required.'
    return errors


def return_loan(loan_id):
    return LoanRepository().mark_returned(loan_id, timezone.localdate())
