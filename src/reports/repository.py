from src.loans.models import Loan


class DjangoMonthlyReportLoanRepository:
    def started_in_period(self, start, end):
        return Loan.objects.filter(lent_on__gte=start, lent_on__lt=end)
