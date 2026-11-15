import datetime

from django.db import migrations, models


def seed_loans(apps, schema_editor):
    Loan = apps.get_model('loans', 'Loan')
    database = schema_editor.connection.alias
    records = [
        {
            'id': 'L1',
            'member': 'ana',
            'isbn': '9780134685991',
            'lent_on': datetime.date(2026, 1, 2),
            'returned_on': None,
        },
        {
            'id': 'L2',
            'member': 'bo',
            'isbn': '9780596007126',
            'lent_on': datetime.date(2026, 1, 10),
            'returned_on': datetime.date(2026, 1, 20),
        },
        {
            'id': 'L3',
            'member': 'cy',
            'isbn': '9781617294945',
            'lent_on': datetime.date(2025, 12, 1),
            'returned_on': datetime.date(2026, 1, 3),
        },
    ]
    for record in records:
        loan_id = record.pop('id')
        Loan.objects.using(database).get_or_create(pk=loan_id, defaults=record)


class Migration(migrations.Migration):
    initial = True

    dependencies = ()

    operations = (
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('member', models.TextField()),
                ('isbn', models.TextField()),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
            options={'ordering': ('id',)},
        ),
        migrations.RunPython(seed_loans, migrations.RunPython.noop),
    )
