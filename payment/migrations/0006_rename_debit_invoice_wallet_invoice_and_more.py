# Generated by Django 4.2 on 2023-08-04 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_rename_tax_invoiceitems_tax_amount_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wallet',
            old_name='debit_invoice',
            new_name='invoice',
        ),
        migrations.RenameField(
            model_name='wallet',
            old_name='transaction_type',
            new_name='type',
        ),
        migrations.AddField(
            model_name='wallet',
            name='desc',
            field=models.TextField(blank=True, null=True),
        ),
    ]
