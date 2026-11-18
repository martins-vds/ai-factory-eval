import csv
from io import StringIO


class InvalidLoan(ValueError):
    def __init__(self, errors):
        self.errors = errors


def lend_loan(repository, member, isbn, lent_on):
    errors = {}
    if not member or not member.strip():
        errors['member'] = 'Enter a member name; blank values are not accepted.'
    if not isbn or not isbn.strip():
        errors['isbn'] = 'Enter an ISBN; blank values are not accepted.'
    if errors:
        raise InvalidLoan(errors)
    return repository.create(member=member, isbn=isbn, lent_on=lent_on)


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


def list_loans_text(repository):
    return ''.join(loan_line(loan) for loan in repository.all())


def get_loan_text(repository, loan_id):
    loan = repository.find(loan_id)
    return loan_line(loan) if loan else None
