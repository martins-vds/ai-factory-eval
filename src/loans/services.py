import csv
from datetime import date
from io import StringIO

from .ports import LoanRecord, LoanStore


class LoanInputError(ValueError):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__('member and isbn are required')


class LoanAlreadyReturned(ValueError):
    pass


def loan_line(loan: LoanRecord):
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


def list_loans_text(loans: LoanStore):
    return ''.join(loan_line(loan) for loan in loans.all())


def get_loan_text(loan_id, loans: LoanStore):
    loan = loans.find(loan_id)
    return loan_line(loan) if loan else None


class LoanService:
    def __init__(self, loans: LoanStore):
        self._loans = loans

    def all(self):
        return self._loans.all()

    def find(self, loan_id):
        return self._loans.find(loan_id)

    def lend(self, member, isbn, on: date):
        field_errors = {}
        if member is None or not member.strip():
            field_errors['member'] = 'This field is required.'
        if isbn is None or not isbn.strip():
            field_errors['isbn'] = 'This field is required.'
        if field_errors:
            raise LoanInputError(field_errors)
        return self._loans.lend(member, isbn, on)

    def mark_returned(self, loan_id, on: date):
        loan = self._loans.find(loan_id)
        if loan is None:
            return None
        if loan.returned_on is not None:
            raise LoanAlreadyReturned
        returned = self._loans.mark_returned(loan_id, on)
        if returned is None:
            raise LoanAlreadyReturned
        return returned

    def list_text(self):
        return list_loans_text(self._loans)

    def detail_text(self, loan_id):
        return get_loan_text(loan_id, self._loans)
