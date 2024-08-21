import json
from decimal import Decimal

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Sum, F
from django.db.models.functions import TruncDate, TruncMonth
from django.http import HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from djmoney.money import Money

from financial_app.forms import CustomUserCreationForm, OperationForm, BudgetForm, BalanceForm, SavingsForm
from financial_app.models import UserProfile, Operation, Budget
from financial_app.utils import get_analytical_data, user_profile_access_required, get_expenses_for_savings, \
    convert_currency, get_cache_data
from django.core.cache import cache

from financial_managment import settings


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("main"))
        else:
            return render(request, "financial/login2.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "financial/login2.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            try:
                user = User.objects.create_user(username, email=email, password=password1)
                user.save()
                user_profile = UserProfile.objects.create(
                    user=user
                )
                Budget.objects.create(user_profile=user_profile)
            except IntegrityError:
                return render(request, "financial/register2.html", {
                    "message": "Username already taken."
                })
            login(request, user)
            return HttpResponseRedirect(reverse("main"))
    else:
        form = CustomUserCreationForm()
    return render(request, "financial/register2.html", {"user_form": form})


def main(request):
    if request.user.is_authenticated:
        analytical_data, currency, user_profile = get_cache_data(request)
        biggest_spending = Operation.objects.filter(user_profile=user_profile).only(
            'amount_of_expenses', 'operation_category', 'created_at').order_by('-amount_of_expenses')[:3]
        savings_form = SavingsForm()
        return render(request, 'financial/main.html',
                      {'analytical_data': analytical_data, 'currency': currency,
                       'biggest_spending': biggest_spending, 'savings_form': savings_form})
    return redirect(reverse('login'))


def recommendations(request):
    analytical_data, currency, _ = get_cache_data(request)
    return render(request, 'financial/recommendations.html', {'analytical_data': analytical_data, 'currency': currency})


@login_required
@user_profile_access_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
    balance_form = BalanceForm(instance=user_profile)
    context = {'user': user, 'user_profile': user_profile, 'balance_form': balance_form}
    return render(request, 'financial/user_profile2.html', context)


@login_required
def create_operation(request):
    if request.method == 'POST':
        operation_form = OperationForm(request.POST)
        if operation_form.is_valid():
            operation = operation_form.save(commit=False)
            request_user_profile = get_object_or_404(UserProfile, user=request.user)
            operation.user_profile = request_user_profile
            # operation.currency = request_user_profile.balance.currency
            budgets = request_user_profile.budgets.filter(disabled=False)
            for budget in budgets:
                if operation.operation_category == budget.budget_category or not budget.budget_category:
                    budget.account -= operation.amount_of_expenses
                    operation.save()
                    operation.budget.add(budget)
                    budget.save()
            request_user_profile.balance -= Money(operation.amount_of_expenses, request_user_profile.balance.currency)
            request_user_profile.save()
            return redirect(reverse('operation_list'))
    else:
        operation_form = OperationForm()
    return render(request, 'financial/create_operation.html', {'operation_form': operation_form})


class OperationListView(LoginRequiredMixin, ListView):
    paginate_by = 6
    model = Operation
    template_name = 'financial/operation_list.html'

    def get_queryset(self):
        self.user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return Operation.objects.filter(
            user_profile=self.user_profile).only('amount_of_expenses', 'operation_category', 'created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currency'] = self.user_profile.balance.currency
        return context


class BudgetListView(LoginRequiredMixin, ListView):
    paginate_by = 2
    model = Budget
    template_name = 'financial/budgets_list.html'

    def get_queryset(self):
        self.request_user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return Budget.budgets.filter(user_profile=self.request_user_profile)\
            .only('budget_category', 'account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.request_user_profile = get_object_or_404(UserProfile, user=self.request.user)
        context['savings_form'] = SavingsForm()
        context['currency'] = self.request_user_profile.balance.currency
        return context


class BudgetFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        request_user_profile = get_object_or_404(UserProfile, user=self.request.user)
        kwargs['user_profile'] = request_user_profile
        return kwargs


class BudgetCreateView(LoginRequiredMixin, BudgetFormMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'financial/create_budget.html'
    success_url = reverse_lazy('budgets_list')

    def form_valid(self, form):
        budget = form.save(commit=False)
        request_user_profile = get_object_or_404(UserProfile, user=self.request.user)
        budget.user_profile = request_user_profile
        main_budget = Budget.budgets.get(budget_category=None, user_profile=request_user_profile)
        if budget.budget_category and main_budget:
            budget.parent = main_budget
        form.save()
        cache.delete(settings.ANALYTICAL_CACHE_NAME)
        return super().form_valid(form)


class BudgetAccessCheckMixin:
    def dispatch(self, request, *args, **kwargs):
        budget = get_object_or_404(Budget.objects.select_related('user_profile'), pk=kwargs['pk'])
        request_user_profile = get_object_or_404(UserProfile, user=request.user)
        if request_user_profile == budget.user_profile:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access denied")


class BudgetUpdateView(LoginRequiredMixin, BudgetAccessCheckMixin, BudgetFormMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'financial/budget_edit.html'

    def get_success_url(self):
        return self.request.get_full_path()

    def form_valid(self, form):
        messages.success(self.request, "The budget was updated successfully.")
        form.is_valid()
        cache.delete(settings.ANALYTICAL_CACHE_NAME)
        return super().form_valid(form)


class BudgetDeleteView(LoginRequiredMixin, BudgetAccessCheckMixin, DeleteView):
    model = Budget
    template_name = 'financial/budget_delete.html'
    success_url = reverse_lazy('budgets_list')

    def form_valid(self, form):
        cache.delete(settings.ANALYTICAL_CACHE_NAME)
        return super().form_valid(form)


@require_POST
@login_required
def update_balance(request, pk):
    user_profile = get_object_or_404(UserProfile, pk=pk)
    currency = user_profile.balance.currency
    balance_form = BalanceForm(request.POST, instance=user_profile)
    if balance_form.is_valid():
        balance_form.save()
        convert_currency(request, currency, balance_form)
    return redirect(reverse('user_profile', kwargs={'username': user_profile.user.username}))


@login_required
@require_GET
def get_budgets(request):
    request_user_profile = get_object_or_404(UserProfile, user=request.user)
    budgets = Budget.budgets.filter(user_profile=request_user_profile).exclude(budget_category=None)
    if budgets:
        budgets_data = [{'account': float(budget.account),
                         'budget_category': budget.budget_category} for budget in budgets]
        return JsonResponse({'status': 'ok', 'budgets': json.dumps(budgets_data)})
    return JsonResponse({'status': 'error'})


@login_required
@require_GET
def get_expenses(request):
    request_user_profile = get_object_or_404(UserProfile, user=request.user)
    current_month = timezone.now().month
    current_year = timezone.now().year
    operations = Operation.objects.filter(user_profile=request_user_profile,
                                          created_at__month=current_month,
                                          created_at__year=current_year)\
        .exclude(operation_category=None).values('operation_category')\
        .annotate(total_operations=Sum('amount_of_expenses'))
    if operations:
        operations_data = [{'amount_of_expenses': float(operation['total_operations']),
                            'operation_category': operation['operation_category']} for operation in operations]
        return JsonResponse({'status': 'ok', 'operations': json.dumps(operations_data)})
    return JsonResponse({'status': 'error'})


@login_required
@require_GET
def get_expenses_by_months(request):
    request_user_profile = get_object_or_404(UserProfile, user=request.user)
    operations = list(Operation.objects.filter(user_profile=request_user_profile)
                      .annotate(month=TruncMonth('created_at'))
                      .values('month')
                      .annotate(total_operations=Sum('amount_of_expenses')))
    if operations:
        operations_data = [{'amount_of_expenses': float(operation['total_operations']),
                            'created_at': operation['month'].strftime("%B")} for operation in operations]
        # print(operations_data)
        return JsonResponse({'status': 'ok', 'operations': json.dumps(operations_data)})
    return JsonResponse({'status': 'error'})


@login_required
@require_POST
def calculate_savings(request):
    request_user_profile = get_object_or_404(UserProfile, user=request.user)
    form = SavingsForm(request.POST)
    data = {}
    if form.is_valid():
        print('ok')
        amount = request.POST.get('amount')
        print(f'budget_categoty - {request.POST.get("budget_category")}, {type(request.POST.get("budget_category"))}')
        budget_category = None if request.POST.get('budget_category') == 'None' else request.POST.get('budget_category')
        budget = get_object_or_404(Budget, budget_category=budget_category, user_profile=request_user_profile, disabled=False)
        expenses_for_savings = get_expenses_for_savings(amount, budget)
        if not expenses_for_savings.get('error'):
            data['expenses_for_savings'] = list(map(float, expenses_for_savings.values()))[0]
            data['currency'] = request_user_profile.balance.currency.code
            return JsonResponse({'status': 'ok', 'saving_data': json.dumps(data)})
        else:
            return JsonResponse({'status': 'error', 'error': json.dumps(expenses_for_savings['error'])})
    return JsonResponse({'status': 'error'})

