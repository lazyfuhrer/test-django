# Generated by Django 4.2 on 2023-10-22 20:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0016_alter_user_email_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('manage_settings', 'Manage Settings'), ('manage_reports', 'Manage Reports'), ('manage_patients', 'Manage Patients'))},
        ),
    ]
