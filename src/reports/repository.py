from collections.abc import Iterable

from src.loans.models import Loan


class DjangoReportLoanRepository:
    def all(self) -> Iterable[Loan]:
        return Loan.objects.all()
