from datetime import date

from django.db import migrations, models


def seed_loans(apps, schema_editor):
    loan_model = apps.get_model('loans', 'Loan')
    for loan in (
        ('L1', 'ana', '9780134685991', date(2026, 1, 2), None),
        ('L2', 'bo', '9780596007126', date(2026, 1, 10), date(2026, 1, 20)),
        ('L3', 'cy', '9781617294945', date(2025, 12, 1), date(2026, 1, 3)),
    ):
        loan_model.objects.get_or_create(
            id=loan[0],
            defaults={
                'member': loan[1],
                'isbn': loan[2],
                'lent_on': loan[3],
                'returned_on': loan[4],
            },
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = ()

    operations = (
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('member', models.TextField()),
                ('isbn', models.TextField()),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
            options={'ordering': ('id',)},
        ),
        migrations.RunPython(seed_loans, migrations.RunPython.noop),
    )
