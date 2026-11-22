from src.fees.composition import fee_application
from src.loans.clock import SystemClock

from .repository import DjangoReportLoanRepository
from .services import MonthlyReportApplication


def monthly_report_application():
    return MonthlyReportApplication(DjangoReportLoanRepository(), fee_application, SystemClock())
