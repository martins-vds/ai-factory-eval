from django.db import connection, transaction

from .models import Loan

_LOAN_ID_LOCK = 0x4C4F414E


class LoanRepository:
    def all(self):
        return Loan.objects.all()

    def find(self, loan_id):
        return Loan.objects.filter(pk=loan_id).first()

    @transaction.atomic
    def create(self, **fields):
        with connection.cursor() as cursor:
            cursor.execute('SELECT pg_advisory_xact_lock(%s)', [_LOAN_ID_LOCK])
        fields['id'] = f'L{Loan.objects.count() + 1}'
        return Loan.objects.create(**fields)

    @transaction.atomic
    def record_return(self, loan_id, today):
        updated = Loan.objects.filter(
            pk=loan_id,
            returned_on__isnull=True,
        ).update(returned_on=today)
        return self.find(loan_id) if updated else None
