from datetime import date

from django.db import migrations


def seed_loans(apps, schema_editor):
    LoanRecord = apps.get_model('loans', 'LoanRecord')
    database = schema_editor.connection.alias
    records = [
        LoanRecord(
            id='L1',
            member='ana',
            isbn='9780134685991',
            lent_on=date(2026, 1, 2),
        ),
        LoanRecord(
            id='L2',
            member='bo',
            isbn='9780596007126',
            lent_on=date(2026, 1, 10),
            returned_on=date(2026, 1, 20),
        ),
        LoanRecord(
            id='L3',
            member='cy',
            isbn='9781617294945',
            lent_on=date(2025, 12, 1),
            returned_on=date(2026, 1, 3),
        ),
    ]
    manager = LoanRecord.objects.using(database)
    if not manager.exists():
        manager.bulk_create(records)


class Migration(migrations.Migration):
    dependencies = (('loans', '0001_initial'),)

    operations = (migrations.RunPython(seed_loans, migrations.RunPython.noop),)
