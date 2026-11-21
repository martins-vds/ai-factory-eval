from collections.abc import Iterable
from datetime import date

from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def started_between(self, start: date, end: date) -> Iterable[Loan]:
        return Loan.objects.filter(lent_on__gte=start, lent_on__lt=end).order_by('member', 'id')
