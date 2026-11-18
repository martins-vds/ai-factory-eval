from src.fees.composition import fee_application
from src.loans.clock import SystemClock

from .repository import DjangoMonthlyReportRepository
from .services import MonthlyReportApplication

monthly_report_application = MonthlyReportApplication(
    DjangoMonthlyReportRepository(),
    SystemClock(),
    fee_application,
)
