from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DjSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('raw_value', models.TextField(blank=True, verbose_name='raw value')),
            ],
            options={
                'verbose_name': 'Django Setting',
                'verbose_name_plural': 'Django Settings',
            },
        ),
    ]
