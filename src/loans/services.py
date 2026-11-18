import csv
from io import StringIO

from .ports import Clock, LoanRecord, LoanRepository


class InvalidLoan(ValueError):
    def __init__(self, fields):
        self.fields = fields
        super().__init__('member and isbn are required')


class LoanAlreadyReturned(ValueError):
    def __init__(self, loan):
        self.loan = loan
        super().__init__('already returned')


class LoanUseCases:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self._loans = loans
        self._clock = clock

    def all(self):
        return self._loans.all()

    def find(self, loan_id: str) -> LoanRecord | None:
        return self._loans.find(loan_id)

    def lend(self, member: str, isbn: str) -> LoanRecord:
        fields = {}
        if not member or not member.strip():
            fields['member'] = 'This field is required.'
        if not isbn or not isbn.strip():
            fields['isbn'] = 'This field is required.'
        if fields:
            raise InvalidLoan(fields)
        return self._loans.lend(member.strip(), isbn.strip(), self._clock.today())

    def return_loan(self, loan_id: str) -> LoanRecord | None:
        loan, updated = self._loans.mark_returned(loan_id, self._clock.today())
        if loan is not None and not updated:
            raise LoanAlreadyReturned(loan)
        return loan


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


def list_loans_text(loans):
    return ''.join(loan_line(loan) for loan in loans)


def get_loan_text(loan):
    return loan_line(loan) if loan else None
