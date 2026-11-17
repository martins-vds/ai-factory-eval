import csv
import io


def loan_line(loan):
    values = [
        loan.id,
        loan.member,
        loan.isbn,
        loan.lent_on.isoformat(),
        loan.due_on.isoformat(),
        loan.returned_on.isoformat() if loan.returned_on else '',
    ]
    output = io.StringIO(newline='')
    csv.writer(output, delimiter=';', lineterminator='', quoting=csv.QUOTE_MINIMAL).writerow(values)
    return output.getvalue()
