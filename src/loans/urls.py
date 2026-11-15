from django.urls import path

from src.loans import views

app_name = 'loans'

urlpatterns = [
    path('loans', views.list_loans, name='list'),
    path('loans/<str:loan_id>', views.get_loan, name='detail'),
    path('ui/loans/', views.catalog, name='ui-list'),
    path('ui/loans/<str:loan_id>/', views.catalog_detail, name='ui-detail'),
]
