from django.urls import path

from src.loans import views

urlpatterns = [
    path('loans', views.list_loans, name='loan-list'),
    path('loans/<str:loan_id>', views.get_loan, name='loan-detail'),
    path('ui/loans/', views.ui_list, name='ui-loan-list'),
    path('ui/loans/<str:loan_id>/', views.ui_detail, name='ui-loan-detail'),
]
