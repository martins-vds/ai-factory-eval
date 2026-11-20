from src.fees.composition import fee_application

from .repository import DjangoReportRepository
from .services import MonthlyReportApplication

monthly_report = MonthlyReportApplication(DjangoReportRepository(), fee_application)
