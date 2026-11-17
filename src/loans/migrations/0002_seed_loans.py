from datetime import date

from django.db import migrations


def seed_loans(apps, schema_editor):
    loan_model = apps.get_model('loans', 'Loan')
    database = schema_editor.connection.alias
    records = [
        ('L1', 'ana', '9780134685991', date(2026, 1, 2), None),
        ('L2', 'bo', '9780596007126', date(2026, 1, 10), date(2026, 1, 20)),
        ('L3', 'cy', '9781617294945', date(2025, 12, 1), date(2026, 1, 3)),
    ]
    for loan_id, member, isbn, lent_on, returned_on in records:
        loan_model.objects.using(database).get_or_create(
            id=loan_id,
            defaults={
                'member': member,
                'isbn': isbn,
                'lent_on': lent_on,
                'returned_on': returned_on,
            },
        )


class Migration(migrations.Migration):
    dependencies = (('loans', '0001_initial'),)

    operations = (migrations.RunPython(seed_loans, migrations.RunPython.noop),)
