from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []  # noqa: RUF012

    operations = [  # noqa: RUF012
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.TextField(primary_key=True, serialize=False)),
                ('member', models.TextField()),
                ('isbn', models.TextField()),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
    ]
