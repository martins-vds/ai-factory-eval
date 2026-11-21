from django.db import models

# Create your models here.
from django.db import models


class LoanRecord(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    member = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255)
    lent_on = models.DateField()
    returned_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['id']
