from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []  # noqa: RUF012

    operations = [  # noqa: RUF012
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('member', models.CharField(max_length=200)),
                ('isbn', models.CharField(max_length=32)),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
    ]
