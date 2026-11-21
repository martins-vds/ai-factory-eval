from django.urls import path

from src.loans import views

urlpatterns = [
    path('loans', views.api_loan_list),
    path('loans/<str:loan_id>', views.api_loan_detail),
    path('ui/loans/', views.loan_catalog, name='loan_catalog'),
    path('ui/loans/<str:loan_id>/', views.ui_loan_detail, name='ui_loan_detail'),
]
