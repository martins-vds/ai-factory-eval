from src.loans.models import Loan


def list_loans():
    return Loan.objects.order_by('pk')


def get_loan(loan_id):
    return Loan.objects.filter(pk=loan_id).first()


def save_loan(loan):
    loan.save()
    return loan
