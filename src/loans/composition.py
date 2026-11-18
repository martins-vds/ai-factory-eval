from django.utils import timezone

from . import services
from .repository import LoanRepository


class LocalClock:
    def today(self):
        return timezone.localdate()


def lend_loan(member, isbn):
    return services.lend_loan(LoanRepository(), LocalClock(), member, isbn)


def return_loan(loan_id):
    return services.return_loan(LoanRepository(), LocalClock(), loan_id)


def list_loans_text():
    return services.list_loans_text(LoanRepository())


def get_loan_text(loan_id):
    return services.get_loan_text(LoanRepository(), loan_id)


def loan_line(loan):
    return services.loan_line(loan)
