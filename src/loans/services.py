import csv
from io import StringIO


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


def lend_loan(repository, member, isbn, lent_on):
    return repository.lend(member, isbn, lent_on)


def return_loan(repository, loan_id, returned_on):
    return repository.mark_returned(loan_id, returned_on)
