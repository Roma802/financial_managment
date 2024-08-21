from datetime import date
from time import timezone

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from djmoney.models.fields import MoneyField
from mptt.models import MPTTModel, TreeForeignKey

CATEGORIES_CHOICES = [
        ("NUTRITION", "Nutrition"),
        ("PUBLIC UTILITIES", "Public utilities"),
        ("PURCHASES", "Purchases"),
        ("FAMILY", "Family"),
        ("TRANSPORT", "Transport"),
        ("HEALTH", "Health"),
        ("EDUCATION", "Education"),
        ("ENTERTAINMENT", "Entertainment"),
        ("PRESENT", "Present"),
        ("INVESTMENTS", "Investments"),
        ("OTHER EXPENSES", "Other expenses")
    ]


class BudgetManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(disabled=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = MoneyField(max_digits=10, decimal_places=2, default_currency='USD', default=0.00, null=True, blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


class Budget(MPTTModel):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    account = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    budget_category = models.CharField(max_length=256, choices=CATEGORIES_CHOICES, null=True, blank=True)
    disabled = models.BooleanField(default=False, null=True, blank=True)
    parent = TreeForeignKey(
        'self',
        related_name='children',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    budgets = BudgetManager()

    class MPTTMeta:
        order_insertion_by = ['-created']

    def __str__(self):
        return f'{self.user_profile.user.username} {self.budget_category if self.budget_category else "total"} ' \
               f'budget for {self.created.strftime("%B")}'

    def save(self, *args, **kwargs):
        user_budgets = Budget.objects.filter(user_profile=self.user_profile, disabled=False)
        if not any(budget.budget_category == self.budget_category and self != budget for budget in user_budgets):
            super().save(*args, **kwargs)


class Operation(models.Model):
    amount_of_expenses = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    # created = models.DateTimeField(auto_now_add=True, db_index=True)
    created_at = models.DateField(default=date.today, db_index=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='operations')
    operation_category = models.CharField(max_length=256, choices=CATEGORIES_CHOICES, null=True, blank=True)
    budget = models.ManyToManyField(Budget)

    class Meta:
        ordering = ['-created_at']

    # def __str__(self):
    #     return f'{self.amount_of_expenses}'

    # def save(self, *args, **kwargs):  # this will have to be changed
    #     if not self.created_at:
    #         self.created_at = timezone.now().date()
    #     return super().save(*args, **kwargs)


