# Generated by Django 4.2 on 2024-03-10 10:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0010_alter_clinicpeople_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0015_alter_invoice_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='clinic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoice_clinic', to='clinic.clinic'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invoice_patient', to=settings.AUTH_USER_MODEL),
        ),
    ]
