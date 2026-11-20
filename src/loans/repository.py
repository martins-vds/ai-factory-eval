from django.db import transaction

from src.loans.models import Loan


class LoanRepository:
    def list(self):
        return list(Loan.objects.order_by('id'))

    def get(self, loan_id):
        return Loan.objects.filter(id=loan_id).first()

    @transaction.atomic
    def save(self, loan):
        loan.save()
        return loan
