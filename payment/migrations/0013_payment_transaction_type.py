# Generated by Django 4.2 on 2024-02-14 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0012_payment_clinic'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='transaction_type',
            field=models.CharField(choices=[('collected', 'Collected'), ('paid', 'Paid')], default='cr', max_length=10),
        ),
    ]
