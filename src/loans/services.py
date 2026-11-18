import csv
from datetime import date
from io import StringIO

from .ports import LoanRecord, LoanStore


class LoanValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('Loan fields are invalid.')


def lend_loan(member: str | None, isbn: str | None, lent_on: date, store: LoanStore) -> LoanRecord:
    errors = {}
    if member is None or not member.strip():
        errors['member'] = 'This field is required.'
    if isbn is None or not isbn.strip():
        errors['isbn'] = 'This field is required.'
    if errors:
        raise LoanValidationError(errors)

    return store.create(id=store.next_id(), member=member, isbn=isbn, lent_on=lent_on)


def loan_line(loan: LoanRecord) -> str:
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


def list_loans_text(store: LoanStore) -> str:
    return ''.join(loan_line(loan) for loan in store.all())


def get_loan_text(loan_id: str, store: LoanStore) -> str | None:
    loan = store.find(loan_id)
    return loan_line(loan) if loan else None
