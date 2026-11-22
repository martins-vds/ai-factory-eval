from src.loans.clock import SystemClock

from .repository import DjangoReportLoanRepository
from .services import MonthlyReportApplication

monthly_report_application = MonthlyReportApplication(DjangoReportLoanRepository(), SystemClock())
