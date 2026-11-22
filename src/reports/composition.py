from src.fees.gateway import HttpPaymentGateway
from src.fees.services import FeeApplication
from src.loans.clock import SystemClock

from .repository import DjangoReportLoanRepository
from .services import MonthlyReportApplication

report_loans = DjangoReportLoanRepository()
report_clock = SystemClock()
report_fees = FeeApplication(report_loans, report_clock, HttpPaymentGateway())
monthly_report_application = MonthlyReportApplication(report_loans, report_clock, report_fees)
