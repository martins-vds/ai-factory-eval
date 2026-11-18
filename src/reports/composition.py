from src.reports.clock import SystemClock
from src.reports.repository import DjangoReportLoanRepository
from src.reports.services import MonthlyReport

monthly_report = MonthlyReport(DjangoReportLoanRepository(), SystemClock())
