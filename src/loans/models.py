from django.db import models


class LoanRecord(models.Model):
    id = models.TextField(primary_key=True)
    member = models.TextField()
    isbn = models.TextField()
    lent_on = models.DateField()
    returned_on = models.DateField(null=True)
