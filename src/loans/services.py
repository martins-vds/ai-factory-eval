import csv
from io import StringIO

from .domain import LoanInputError, LoanNotFound
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

        return self.loans.lend(member, isbn, lent_on)

    def return_loan(self, loan_id, returned_on):
        loan = self.loans.find(loan_id)
        if loan is None:
            raise LoanNotFound
        loan.mark_returned(returned_on)
        return self.loans.save_returned(loan)


def list_loans_text(application):
    return ''.join(loan_line(loan) for loan in application.all_loans())


def get_loan_text(loan_id, application):
    loan = application.find_loan(loan_id)
    return loan_line(loan) if loan else None
