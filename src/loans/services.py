import csv
import io
from datetime import timedelta


def due_date(lent_on):
    return lent_on + timedelta(days=14)


def format_loan(loan):
    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='')
    writer.writerow(
        [
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            due_date(loan.lent_on).isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
    )
    return output.getvalue()
