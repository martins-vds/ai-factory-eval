import csv
from io import StringIO


def loan_line(loan):
    output = StringIO(newline='')
    csv.writer(output, delimiter=';', lineterminator='\n').writerow(
        [
            loan.pk,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return output.getvalue()
