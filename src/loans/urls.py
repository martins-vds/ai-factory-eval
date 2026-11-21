from django.urls import path

from src.loans import views

urlpatterns = [
    path('loans', views.loans, name='loans'),
    path('loans/<str:loan_id>', views.loan_detail, name='loan-detail'),
    path('ui/loans/', views.loan_list_ui, name='loan-list-ui'),
    path('ui/loans/<str:loan_id>/', views.loan_detail_ui, name='loan-detail-ui'),
]
