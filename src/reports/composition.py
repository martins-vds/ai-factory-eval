from src.fees.composition import fee_application
from src.loans.clock import SystemClock

from .repository import DjangoReportLoanRepository
from .services import MonthlyReportApplication

monthly_report_application = MonthlyReportApplication(
    DjangoReportLoanRepository(),
    fee_application,
    SystemClock(),
)
