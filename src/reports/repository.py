from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def loans_started_between(self, start, end):
        return Loan.objects.filter(lent_on__gte=start, lent_on__lt=end)
