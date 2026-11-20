from .repository import DjangoReportRepository
from .services import MonthlyReportApplication

monthly_report = MonthlyReportApplication(DjangoReportRepository())
