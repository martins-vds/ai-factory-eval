from django.urls import path

from src.loans import views

urlpatterns = [
    path('loans', views.loan_list, name='loan_list'),
    path('loans/<str:loan_id>', views.loan_detail, name='loan_detail'),
    path('ui/loans/', views.loan_catalog_page, name='loan_catalog'),
    path('ui/loans/<str:loan_id>/', views.loan_page, name='loan_page'),
]
