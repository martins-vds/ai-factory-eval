from datetime import date
from typing import ClassVar

from django.db import migrations, models


def seed_loans(apps, schema_editor):
    Loan = apps.get_model('loans', 'Loan')
    database = schema_editor.connection.alias
    seeds = (
        ('L1', 'ana', '9780134685991', date(2026, 1, 2), None),
        ('L2', 'bo', '9780596007126', date(2026, 1, 10), date(2026, 1, 20)),
        ('L3', 'cy', '9781617294945', date(2025, 12, 1), date(2026, 1, 3)),
    )
    for loan_id, member, isbn, lent_on, returned_on in seeds:
        Loan.objects.using(database).get_or_create(
            id=loan_id,
            defaults={
                'member': member,
                'isbn': isbn,
                'lent_on': lent_on,
                'returned_on': returned_on,
            },
        )


class Migration(migrations.Migration):
    initial = True

    dependencies: ClassVar[list] = []

    operations: ClassVar[list] = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('member', models.CharField(max_length=255)),
                ('isbn', models.CharField(max_length=255)),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.RunPython(seed_loans, migrations.RunPython.noop),
    ]
