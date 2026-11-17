from datetime import date

from django.db.models import Q

from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def loans_with_activity(self, start: date, end: date):
        return Loan.objects.filter(
            Q(lent_on__gte=start, lent_on__lt=end) | Q(returned_on__gte=start, returned_on__lt=end)
        ).order_by()
