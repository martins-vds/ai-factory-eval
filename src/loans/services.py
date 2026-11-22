import csv
from io import StringIO

from .domain import Loan, LoanInputError, LoanNotFound
from .ports import LoanStore


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


class LoanApplication:
    def __init__(self, loans: LoanStore):
        self.loans = loans

    def all_loans(self):
        return self.loans.all()

    def find_loan(self, loan_id):
        return self.loans.find(loan_id)

    def lend(self, member, isbn, lent_on):
        errors = {
            field: 'This field is required.'
            for field, value in (('member', member), ('isbn', isbn))
            if value is None or not value.strip()
        }
        if errors:
            raise LoanInputError(errors)

        loan = Loan(
            id=f'L{len(self.loans.all()) + 1}',
            member=member,
            isbn=isbn,
            lent_on=lent_on,
        )
        return self.loans.add(loan)

    def return_loan(self, loan_id, returned_on):
        loan = self.loans.find(loan_id)
        if loan is None:
            raise LoanNotFound
        loan.mark_returned(returned_on)
        return self.loans.save_returned(loan)
