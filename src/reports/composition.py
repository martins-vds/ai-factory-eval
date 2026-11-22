from src.fees.services import FeeApplication
from src.loans.clock import SystemClock

from .repository import DjangoReportLoanRepository
from .services import MonthlyReportApplication


class UnusedPaymentGateway:
    def charge(self, loan_id):
        raise RuntimeError('Monthly reporting cannot process payments')


def monthly_report_application():
    clock = SystemClock()
    loans = DjangoReportLoanRepository()
    fees = FeeApplication(loans, clock, UnusedPaymentGateway())
    return MonthlyReportApplication(loans, fees, clock)
