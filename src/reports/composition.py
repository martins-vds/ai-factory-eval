from .clock import SystemClock
from .repository import DjangoMonthlyReportRepository
from .services import MonthlyReport

monthly_report = MonthlyReport(DjangoMonthlyReportRepository(), SystemClock())
