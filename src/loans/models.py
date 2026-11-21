from datetime import date, timedelta

from django.db import connection, models


class Loan(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    member = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255)
    lent_on = models.DateField()
    due_on = models.DateField()
    returned_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ('id',)

    def save(self, *args, **kwargs):
        self.due_on = self.lent_on + timedelta(days=14)
        super().save(*args, **kwargs)


def seed_records_if_empty():
    try:
        if Loan.objects.exists():
            return
    except Exception:
        return

    Loan.objects.bulk_create(
        [
            Loan(
                id='L1',
                member='ana',
                isbn='9780134685991',
                lent_on=date(2026, 1, 2),
                due_on=date(2026, 1, 16),
            ),
            Loan(
                id='L2',
                member='bo',
                isbn='9780596007126',
                lent_on=date(2026, 1, 10),
                due_on=date(2026, 1, 24),
                returned_on=date(2026, 1, 20),
            ),
            Loan(
                id='L3',
                member='cy',
                isbn='9781617294945',
                lent_on=date(2025, 12, 1),
                due_on=date(2025, 12, 15),
                returned_on=date(2026, 1, 3),
            ),
        ]
    )
