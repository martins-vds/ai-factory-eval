from django.urls import path

from . import views

urlpatterns = [
    path('loans', views.loan_list, name='loan-list'),
    path('loans/<str:loan_id>', views.loan_detail, name='loan-detail'),
    path('ui/loans/', views.ui_loan_list, name='ui-loan-list'),
    path('ui/loans/<str:loan_id>/', views.ui_loan_detail, name='ui-loan-detail'),
]
