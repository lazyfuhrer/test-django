# Generated by Django 4.2 on 2024-02-14 20:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0013_payment_transaction_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.invoice'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_type',
            field=models.CharField(choices=[('collected', 'Collected'), ('paid', 'Paid')], default='collected', max_length=10),
        ),
    ]
