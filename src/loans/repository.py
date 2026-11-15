from .models import Loan


def list_loans():
    return list(Loan.objects.order_by('id'))


def get_loan(loan_id):
    return Loan.objects.filter(pk=loan_id).first()
