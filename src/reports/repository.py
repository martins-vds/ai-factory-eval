from datetime import date

from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def loans_started_between(self, start: date, end: date):
        return Loan.objects.filter(lent_on__gte=start, lent_on__lt=end).only(
            'member',
            'lent_on',
            'returned_on',
        )

    def loans_returned_between(self, start: date, end: date):
        return Loan.objects.filter(returned_on__gte=start, returned_on__lt=end).only(
            'member',
            'lent_on',
            'returned_on',
        )
