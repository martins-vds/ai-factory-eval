import csv
import io
from datetime import timedelta


class CatalogService:
    def __init__(self, repository=None):
        self.repository = repository

    def due_on(self, loan):
        return loan.lent_on + timedelta(days=14)

    def export_line(self, loan):
        fields = [
            loan.id,
            loan.member,
            loan.isbn,
            loan.lent_on.isoformat(),
            self.due_on(loan).isoformat(),
            loan.returned_on.isoformat() if loan.returned_on else '',
        ]
        output = io.StringIO(newline='')
        writer = csv.writer(output, delimiter=';', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fields)
        return output.getvalue()

    def list_loans(self):
        if self.repository is None:
            raise RuntimeError('A loan repository is required')
        return self.repository.list()

    def get_loan(self, loan_id):
        if self.repository is None:
            raise RuntimeError('A loan repository is required')
        return self.repository.get(loan_id)
