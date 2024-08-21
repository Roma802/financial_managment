from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Q

from financial_app.models import Operation, Budget, UserProfile, CATEGORIES_CHOICES


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'type': 'text',
            'name': 'username',
            'placeholder': 'Username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email',
            'name': 'email',
            'placeholder': 'Email Address'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'name': 'password',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'name': 'confirmation',
            'placeholder': 'Confirmation your password'
        })

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ['amount_of_expenses', 'operation_category']
        widgets = {
            'amount_of_expenses': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'operation_category': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_amount_of_expenses(self):
        amount_of_expenses = self.cleaned_data.get('amount_of_expenses')
        if amount_of_expenses <= 0:
            raise ValidationError('Your amount should be more than 0.')
        return amount_of_expenses


class BalanceForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['balance']


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['budget_category', 'account']

        widgets = {
            'account': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'budget_category': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.budget_category is None:
            if self.initial:
                self.fields['budget_category'].widget.attrs['disabled'] = 'disabled'

    def clean_budget_category(self):
        category = self.cleaned_data.get('budget_category')
        user_budgets = Budget.objects.filter(user_profile=self.user_profile, disabled=False)
        print(any(budget.budget_category == category and budget != self.instance for budget in user_budgets))
        if any(budget.budget_category == category and budget != self.instance for budget in user_budgets):
            raise ValidationError('You have to choose unique category.')
        return category


class SavingsForm(forms.Form):
    amount = forms.FloatField(label='the amount you want to set aside')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs.update({
            'type': 'text',
            'class': 'amount',
            'placeholder': 'Amount'
        })

    # def clean_amount(self):
    #     amount = self.cleaned_data.get('amount')
    #     print(amount, type(amount))
    #     if amount <= 0:
    #         # raise ValidationError('the amount must be greater than zero')
    #         print('here')
    #         self.add_error('amount', 'The amount must be greater than zero')
    #     return amount

