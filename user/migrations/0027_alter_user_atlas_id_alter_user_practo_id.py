# Generated by Django 4.2.13 on 2024-07-28 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0026_alter_address_city_alter_address_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='atlas_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='practo_id',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
