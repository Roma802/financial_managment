from datetime import timedelta

from celery import Celery, shared_task

from financial_app.models import Budget, UserProfile


@shared_task
def update_budgets():
    Budget.objects.exclude(budget_category=None).delete()
    Budget.objects.filter(budget_category=None).update(disabled=True)
    all_user_profiles = UserProfile.objects.all()
    for user_profile in all_user_profiles:
        Budget.objects.create(user_profile=user_profile)



