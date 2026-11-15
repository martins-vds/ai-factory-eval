from datetime import date

from django.db import migrations, models


def seed_loans(apps, schema_editor):
    Loan = apps.get_model('loans', 'Loan')
    database = schema_editor.connection.alias
    manager = Loan.objects.using(database)
    if manager.exists():
        return
    manager.bulk_create(
        [
            Loan(
                id='L1',
                member='ana',
                isbn='9780134685991',
                lent_on=date(2026, 1, 2),
            ),
            Loan(
                id='L2',
                member='bo',
                isbn='9780596007126',
                lent_on=date(2026, 1, 10),
                returned_on=date(2026, 1, 20),
            ),
            Loan(
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

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('member', models.CharField(max_length=255)),
                ('isbn', models.CharField(max_length=64)),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.RunPython(seed_loans, migrations.RunPython.noop),
    ]
