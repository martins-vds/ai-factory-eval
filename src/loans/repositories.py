from src.loans.models import Loan


def list_loans():
    return Loan.objects.order_by('id')
