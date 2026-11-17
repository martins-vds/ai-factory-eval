from datetime import timedelta
from typing import ClassVar

from django.db import models


class Loan(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    member = models.TextField()
    isbn = models.TextField()
    lent_on = models.DateField()
    returned_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering: ClassVar = ['id']

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)
