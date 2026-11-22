from src.fees.gateway import HttpPaymentGateway
from src.fees.services import FeeApplication
from src.loans.clock import SystemClock

from .repository import DjangoReportLoanRepository
from .services import MonthlyReportApplication

repository = DjangoReportLoanRepository()
clock = SystemClock()
monthly_report_application = MonthlyReportApplication(
    repository,
    FeeApplication(repository, clock, HttpPaymentGateway()),
    clock,
)
