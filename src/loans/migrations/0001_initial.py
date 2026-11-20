from datetime import date
from typing import ClassVar

from django.db import migrations, models


def seed_example_loans(apps, schema_editor):
    loan_record = apps.get_model('loans', 'LoanRecord')
    loan_record.objects.bulk_create(
        [
            loan_record(
                id='L1',
                member='ana',
                isbn='9780134685991',
                lent_on=date(2026, 1, 2),
            ),
            loan_record(
                id='L2',
                member='bo',
                isbn='9780596007126',
                lent_on=date(2026, 1, 10),
                returned_on=date(2026, 1, 20),
            ),
            loan_record(
                id='L3',
                member='cy',
                isbn='9781617294945',
                lent_on=date(2025, 12, 1),
                returned_on=date(2026, 1, 3),
            ),
        ]
    )


class Migration(migrations.Migration):
    initial = True

    dependencies: ClassVar[list] = []

    operations: ClassVar[list] = [
        migrations.CreateModel(
            name='LoanRecord',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('member', models.TextField()),
                ('isbn', models.TextField()),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'loans',
                'ordering': ['id'],
            },
        ),
        migrations.RunPython(seed_example_loans, migrations.RunPython.noop),
    ]
