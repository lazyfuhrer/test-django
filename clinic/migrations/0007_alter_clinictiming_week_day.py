# Generated by Django 4.2 on 2023-06-10 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0006_rename_beak_2_end_clinictiming_break_2_end_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinictiming',
            name='week_day',
            field=models.CharField(choices=[('sunday', 'Sunday'), ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday')], null=True),
        ),
    ]
