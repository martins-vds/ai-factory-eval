from django.urls import path

from . import views

urlpatterns = [
    path('loans', views.api_loan_list, name='api-loan-list'),
    path('loans/<str:loan_id>', views.api_loan_detail, name='api-loan-detail'),
    path('ui/loans/', views.ui_loan_list, name='ui-loan-list'),
    path('ui/loans/<str:loan_id>/', views.ui_loan_detail, name='ui-loan-detail'),
]
