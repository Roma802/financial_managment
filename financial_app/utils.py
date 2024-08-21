import calendar
from datetime import datetime
from decimal import Decimal

import requests
from django.contrib import messages
from django.core.cache import cache
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from financial_app.models import UserProfile, Budget, Operation
from financial_managment import settings
from financial_managment.settings import API_KEY


def get_analytical_data(user_budgets):
    current_date = datetime.now().date()
    last_day_of_month = calendar.monthrange(current_date.year, current_date.month)[1]
    remaining_days = last_day_of_month - datetime.now().day
    context = []
    # print(remaining_days)
    for budget in user_budgets:
        if budget and budget.account >= 0 and remaining_days != 0:
            allowable_expenses_per_day = budget.account / remaining_days
            allowable_expenses_per_day = round(allowable_expenses_per_day, 2)
            # context.update({budget.budget_category: allowable_expenses_per_day})
            context.append((budget.budget_category, allowable_expenses_per_day))
    return context


def get_expenses_for_savings(amount_of_savings, budget):
    current_date = datetime.now().date()
    last_day_of_month = calendar.monthrange(current_date.year, current_date.month)[1]
    remaining_days = last_day_of_month - datetime.now().day
    context = {}
    amount_of_savings_decimal = Decimal(amount_of_savings)
    if budget.account >= amount_of_savings_decimal:
        if remaining_days != 0:
            allowable_expenses_per_day = (budget.account - amount_of_savings_decimal) / remaining_days
            allowable_expenses_per_day = round(allowable_expenses_per_day, 2)
            context = {budget.budget_category: allowable_expenses_per_day}
        else:
            context = {'error': 'The month is over.'}
    else:
        context = {'error': 'Budget should be greater than savings.'}
    return context


def user_profile_access_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        user = request.user
        user_profile = get_object_or_404(UserProfile.objects.select_related('user'), user=user)
        if user_profile.user.username == kwargs['username']:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access denied")
    return wrapped_view


def convert_currency(request, currency, balance_form):
    balance = balance_form.cleaned_data.get('balance')
    if balance.currency != currency:
        response = None
        try:
            params = {'access_key': API_KEY, 'symbols': f'{balance.currency}, {currency}'}
            json_response = requests.get(f'http://api.exchangeratesapi.io/v1/latest', params=params)
            response = json_response.json()
        except requests.exceptions.RequestException as e:
            print(e)
        if response and response.get('success'):
            last_currency = response.get('rates').get(str(currency))
            new_currency = response.get('rates').get(str(balance.currency))
            if last_currency and new_currency:
                ratio_of_currencies = Decimal(new_currency)/Decimal(last_currency)
                user_profile = balance_form.save(commit=False)
                user_profile.balance.amount = ratio_of_currencies * balance.amount
                user_profile.save()
                request_user_profile = get_object_or_404(UserProfile, user=request.user)
                user_budgets = Budget.objects.filter(user_profile=request_user_profile, disabled=False)\
                    .update(account=F('account') * ratio_of_currencies)
                user_operations = Operation.objects.filter(user_profile=request_user_profile)\
                    .update(amount_of_expenses=F('amount_of_expenses') * ratio_of_currencies)
                messages.success(request, 'Currency was updated successfully.')
            else:
                messages.error(request, "Conversion hasn't occurred.")
        else:
            messages.error(request, "Conversion hasn't occurred.")


def get_cache_data(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    analytical_cache_data = cache.get(settings.ANALYTICAL_CACHE_NAME)
    if analytical_cache_data:
        analytical_data = analytical_cache_data
    else:
        user_budgets = Budget.objects.filter(user_profile=user_profile, disabled=False)
        analytical_data = get_analytical_data(user_budgets)
        cache.set(settings.ANALYTICAL_CACHE_NAME, analytical_data, 1800)
    currency = user_profile.balance.currency
    return analytical_data, currency, user_profile

