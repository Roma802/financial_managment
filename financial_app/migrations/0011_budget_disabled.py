# Generated by Django 4.2.11 on 2024-04-01 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial_app', '0010_alter_budget_budget_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='disabled',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]