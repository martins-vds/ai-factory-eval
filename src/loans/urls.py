from django.urls import path

from src.loans import views

urlpatterns = [
    path('loans', views.api_list, name='api_loan_list'),
    path('loans/<str:loan_id>', views.api_detail, name='api_loan_detail'),
    path('ui/loans/', views.ui_list, name='ui_loan_list'),
    path('ui/loans/<str:loan_id>/', views.ui_detail, name='ui_loan_detail'),
]
