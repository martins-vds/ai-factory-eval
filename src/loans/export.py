import csv
import io


def export_loans(loans):
    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    writer.writerows(
        [
            [
                loan.pk,
                loan.member,
                loan.isbn,
                loan.lent_on.isoformat(),
                loan.due_on.isoformat(),
                loan.returned_on.isoformat() if loan.returned_on else '',
            ]
            for loan in loans
        ]
    )
    return output.getvalue()
