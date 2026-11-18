from src.loans.clock import SystemClock

from .repository import DjangoMonthlyReportRepository
from .services import MonthlyReportApplication

monthly_report_application = MonthlyReportApplication(
    DjangoMonthlyReportRepository(),
    SystemClock(),
)
