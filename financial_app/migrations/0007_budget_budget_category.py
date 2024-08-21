# Generated by Django 4.2.11 on 2024-03-24 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial_app', '0006_alter_budget_options_budget_level_budget_lft_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='budget_category',
            field=models.CharField(blank=True, choices=[('NUTRITION', 'Nutrition'), ('PUBLIC UTILITIES', 'Public utilities'), ('PURCHASES', 'Purchases'), ('FAMILY', 'Family'), ('TRANSPORT', 'Transport'), ('HEALTH', 'Health'), ('EDUCATION', 'Education'), ('ENTERTAINMENT', 'Entertainment'), ('PRESENT', 'Present'), ('INVESTMENTS', 'Investments'), ('OTHER EXPENSES', 'Other expenses')], max_length=256, null=True, unique=True),
        ),
    ]