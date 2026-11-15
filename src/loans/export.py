import csv
import io


def loan_line(loan):
    output = io.StringIO(newline='')
    returned_on = loan.returned_on.isoformat() if loan.returned_on else ''
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    writer.writerow(
        [
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            loan.due_on.isoformat(),
            returned_on,
        ]
    )
    return output.getvalue()
