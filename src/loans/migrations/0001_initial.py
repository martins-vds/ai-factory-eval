from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = ()

    operations = (
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('member', models.CharField(max_length=255)),
                ('isbn', models.CharField(max_length=255)),
                ('lent_on', models.DateField()),
                ('returned_on', models.DateField(blank=True, null=True)),
            ],
            options={'ordering': ('id',)},
        ),
    )
