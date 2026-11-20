from src.fees.composition import fee_application
from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .services import MonthlyReportApplication

monthly_report_application = MonthlyReportApplication(
    DjangoLoanRepository(),
    SystemClock(),
    fee_application,
)
