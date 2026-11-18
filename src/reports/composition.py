from src.fees.composition import fee_application

from .repository import DjangoMonthlyReportLoanRepository
from .services import MonthlyReportApplication

monthly_report_application = MonthlyReportApplication(
    DjangoMonthlyReportLoanRepository(),
    fee_application,
)
