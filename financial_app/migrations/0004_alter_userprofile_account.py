# Generated by Django 4.2.11 on 2024-03-17 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial_app', '0003_alter_category_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='account',
            field=models.FloatField(default=0.0),
        ),
    ]
