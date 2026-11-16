import datetime

from django.db import migrations, models


def load_seed_loans(apps, schema_editor):
    loan_model = apps.get_model('loans', 'Loan')
    loans = [
        ('L1', 'ana', '9780134685991', datetime.date(2026, 1, 2), None),
        ('L2', 'bo', '9780596007126', datetime.date(2026, 1, 10), datetime.date(2026, 1, 20)),
        ('L3', 'cy', '9781617294945', datetime.date(2025, 12, 1), datetime.date(2026, 1, 3)),
    ]
    for loan_id, member, isbn, lent_on, returned_on in loans:
        loan_model.objects.get_or_create(
            pk=loan_id,
            defaults={
                'member': member,
                'isbn': isbn,
                'lent_on': lent_on,
                'returned_on': returned_on,
            },
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = ()

    operations = (
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('member', models.TextField()),
                ('isbn', models.TextField()),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.RunPython(load_seed_loans, migrations.RunPython.noop),
    )
