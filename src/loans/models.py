from datetime import timedelta

from django.db import models


class Loan(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    member = models.CharField(max_length=200)
    isbn = models.CharField(max_length=32)
    lent_on = models.DateField()
    returned_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['pk']  # noqa: RUF012

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)
