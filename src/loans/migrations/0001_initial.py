from django.db import migrations, models


def seed_loans(apps, schema_editor):
    Loan = apps.get_model('loans', 'Loan')
    if Loan.objects.exists():
        return
    Loan.objects.bulk_create(
        [
            Loan(
                id='L1',
                member='ana',
                isbn='9780134685991',
                lent_on='2026-01-02',
                due_on='2026-01-16',
            ),
            Loan(
                id='L2',
                member='bo',
                isbn='9780596007126',
                lent_on='2026-01-10',
                due_on='2026-01-24',
                returned_on='2026-01-20',
            ),
            Loan(
                id='L3',
                member='cy',
                isbn='9781617294945',
                lent_on='2025-12-01',
                due_on='2025-12-15',
                returned_on='2026-01-03',
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
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('member', models.CharField(max_length=255)),
                ('isbn', models.CharField(max_length=255)),
                ('lent_on', models.DateField()),
                ('due_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
            options={'ordering': ('id',)},
        ),
        migrations.RunPython(seed_loans, migrations.RunPython.noop),
    ]
