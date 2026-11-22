import csv
from io import StringIO

from .ports import Clock, LoanRecord, LoanStore


class LoanInputError(ValueError):
    def __init__(self, errors):
        self.errors = errors


class LoanNotFound(LookupError):
    def __init__(self):
        super().__init__('no such loan')


class LoanAlreadyReturned(ValueError):
    def __init__(self):
        super().__init__('loan already returned')


class LoanApplication:
    def __init__(self, loan_store: LoanStore, clock: Clock):
        self.loan_store = loan_store
        self.clock = clock

    def all(self):
        return self.loan_store.all()

    def find(self, loan_id):
        return self.loan_store.find(loan_id)

    def lend(self, member, isbn):
        errors = {
            field: 'This field cannot be blank.'
            for field, value in (('member', member), ('isbn', isbn))
            if value is None or not value.strip()
        }
        if errors:
            raise LoanInputError(errors)
        return self.loan_store.create(
            member=member,
            isbn=isbn,
            lent_on=self.clock.today(),
        )

    def return_loan(self, loan_id):
        loan = self.loan_store.find(loan_id)
        if loan is None:
            raise LoanNotFound()
        if loan.returned_on is not None:
            raise LoanAlreadyReturned()
        returned = self.loan_store.mark_returned(loan_id, self.clock.today())
        if returned is None:
            raise LoanAlreadyReturned()
        return returned


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


def list_loans_text(loans):
    return ''.join(loan_line(loan) for loan in loans)


def get_loan_text(loan):
    return loan_line(loan) if loan else None
