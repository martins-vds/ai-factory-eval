from datetime import date

from django.db import migrations


SEED_LOANS = (
    ('L1', 'ana', '9780134685991', date(2026, 1, 2), None),
    ('L2', 'bo', '9780596007126', date(2026, 1, 10), date(2026, 1, 20)),
    ('L3', 'cy', '9781617294945', date(2025, 12, 1), date(2026, 1, 3)),
)


def seed_loans(apps, schema_editor):
    loan_record = apps.get_model('loans', 'LoanRecord')
    for loan_id, member, isbn, lent_on, returned_on in SEED_LOANS:
        loan_record.objects.using(schema_editor.connection.alias).get_or_create(
            id=loan_id,
            defaults={
                'member': member,
                'isbn': isbn,
                'lent_on': lent_on,
                'returned_on': returned_on,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('loans', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_loans, migrations.RunPython.noop),
    ]
