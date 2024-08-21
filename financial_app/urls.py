import debug_toolbar
from django.urls import path, include, re_path
from rest_framework.authtoken import views as rest_views
from financial_app import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path('main/', views.main, name='main'),
    path('user_profile/<slug:username>', views.user_profile, name='user_profile'),
    path('create_operation/', views.create_operation, name='create_operation'),
    path('operation/', views.OperationListView.as_view(), name='operation_list'),
    path('budget/', views.BudgetListView.as_view(), name='budgets_list'),
    path('create_budget/', views.BudgetCreateView.as_view(), name='create_budget'),
    path('update_budget/<int:pk>', views.BudgetUpdateView.as_view(), name='update_budget'),
    path('delete_budget/<int:pk>', views.BudgetDeleteView.as_view(), name='delete_budget'),
    path('update_balance/<int:pk>', views.update_balance, name='update_balance'),
    path('get_budgets/', views.get_budgets, name='get_budgets'),
    path('get_expenses/', views.get_expenses, name='get_expenses'),
    path('get_expenses_by_months/', views.get_expenses_by_months, name='get_expenses_by_month'),
    path('calculate_savings/', views.calculate_savings, name='calculate_savings'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('__debug__', include(debug_toolbar.urls))
    # path('api/v1/auth', include('djoser.urls')),
    # re_path(r'^auth/', include('djoser.urls.authtoken')),
]
