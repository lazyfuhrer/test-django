# Generated by Django 4.2 on 2023-05-31 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_doctortiming_doctorleave_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='doctor_calender_color',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
