from datetime import date

from django.db import migrations, models


def seed_loans(apps, schema_editor):
    loan_model = apps.get_model('loans', 'Loan')
    database = schema_editor.connection.alias
    loan_model.objects.using(database).bulk_create(
        [
            loan_model(
                id='L1',
                member='ana',
                isbn='9780134685991',
                lent_on=date(2026, 1, 2),
            ),
            loan_model(
                id='L2',
                member='bo',
                isbn='9780596007126',
                lent_on=date(2026, 1, 10),
                returned_on=date(2026, 1, 20),
            ),
            loan_model(
                id='L3',
                member='cy',
                isbn='9781617294945',
                lent_on=date(2025, 12, 1),
                returned_on=date(2026, 1, 3),
            ),
        ],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('member', models.TextField()),
                ('isbn', models.TextField()),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.RunPython(seed_loans, migrations.RunPython.noop),
    ]
