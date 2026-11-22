from datetime import timedelta

from src.loans.domain import Loan


def loan_due_date(loan: Loan):
    return loan.lent_on + timedelta(days=14)
