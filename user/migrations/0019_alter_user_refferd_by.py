# Generated by Django 4.2 on 2023-11-20 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_user_national_id_user_patient_notes_user_practo_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='refferd_by',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
    ]
