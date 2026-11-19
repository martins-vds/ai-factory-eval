from src.loans.clock import SystemClock

from .repository import DjangoReportLoanRepository
from .services import MonthlyReport

monthly_report = MonthlyReport(DjangoReportLoanRepository(), SystemClock())
