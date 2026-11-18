from datetime import date

from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def started_between(self, start: date, end: date):
        return Loan.objects.filter(lent_on__gte=start, lent_on__lt=end)

    def returned_between(self, start: date, end: date):
        return Loan.objects.filter(returned_on__gte=start, returned_on__lt=end)
