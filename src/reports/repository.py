from src.loans.models import Loan


class DjangoMonthlyReportRepository:
    def started_between(self, start, end):
        return Loan.objects.filter(lent_on__gte=start, lent_on__lt=end).order_by('id')

    def returned_between(self, start, end):
        return Loan.objects.filter(returned_on__gte=start, returned_on__lt=end).order_by('id')
