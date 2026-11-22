from django.urls import path

from . import views

urlpatterns = [
    path('loans', views.loans),
    path('loans/<str:loan_id>/return', views.loan_return),
    path('loans/<str:loan_id>', views.loan_detail),
    path('ui/loans/', views.loan_catalog),
    path('ui/loans/new/', views.loan_lend_page, name='loan-lend-page'),
    path('ui/loans/<str:loan_id>/return/', views.loan_return_from_page, name='loan-return-page'),
    path('ui/loans/<str:loan_id>/', views.loan_catalog_detail, name='loan-catalog-detail'),
]
