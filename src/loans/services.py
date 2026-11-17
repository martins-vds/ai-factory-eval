import csv
from io import StringIO


def export_loans(loans):
    output = StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    for loan in loans:
        writer.writerow(
            (
                loan.id,
                loan.member,
                loan.isbn,
                loan.lent_on.isoformat(),
                loan.due_on.isoformat(),
                loan.returned_on.isoformat() if loan.returned_on else '',
            )
        )
    return output.getvalue()
