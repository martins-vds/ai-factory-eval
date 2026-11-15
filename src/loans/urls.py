from django.urls import path

from src.loans import views

urlpatterns = [
    path('loans', views.loan_list, name='loan-list'),
    path('loans/<str:loan_id>', views.loan_detail, name='loan-detail'),
    path('ui/loans/', views.loan_catalog, name='ui-loan-list'),
    path('ui/loans/<str:loan_id>/', views.loan_page, name='ui-loan-detail'),
]
