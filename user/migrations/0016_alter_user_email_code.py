# Generated by Django 4.2 on 2023-10-11 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_remove_doctorleave_end_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email_code',
            field=models.TextField(blank=True, default=None, max_length=255, null=True, verbose_name='Email Verify Code'),
        ),
    ]
