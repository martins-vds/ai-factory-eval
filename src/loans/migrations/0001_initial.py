from django.db import migrations, models


def seed_loans(apps, schema_editor):
    Loan = apps.get_model('loans', 'Loan')
    seeds = [
        ('L1', 'ana', '9780134685991', '2026-01-02', None),
        ('L2', 'bo', '9780596007126', '2026-01-10', '2026-01-20'),
        ('L3', 'cy', '9781617294945', '2025-12-01', '2026-01-03'),
    ]
    for loan_id, member, isbn, lent_on, returned_on in seeds:
        Loan.objects.get_or_create(
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

    dependencies = ()

    operations = (
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.TextField(primary_key=True, serialize=False)),
                ('member', models.TextField()),
                ('isbn', models.TextField()),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.RunPython(seed_loans, migrations.RunPython.noop),
    )
