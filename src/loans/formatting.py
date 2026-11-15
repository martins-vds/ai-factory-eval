import csv
from io import StringIO


def _fields(loan):
    return (
        loan.id,
        loan.member,
        loan.isbn,
        loan.lent_on.isoformat(),
        loan.due_on.isoformat(),
        loan.returned_on.isoformat() if loan.returned_on else '',
    )


def format_loan(loan):
    output = StringIO(newline='')
    csv.writer(output, delimiter=';', lineterminator='\n').writerow(_fields(loan))
    return output.getvalue()


def format_loans(loans):
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    writer.writerows(_fields(loan) for loan in loans)
    return output.getvalue()
