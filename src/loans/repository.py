from contextlib import contextmanager

from django.db import transaction

from src.loans.models import Loan


class LoanRepository:
    @contextmanager
    def transaction(self):
        with transaction.atomic():
            yield self

    def all(self):
        return list(Loan.objects.order_by('pk'))

    def get(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()
