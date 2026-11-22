from src.loans.models import Loan


class DjangoReportLoanRepository:
    def all(self):
        return Loan.objects.all()
