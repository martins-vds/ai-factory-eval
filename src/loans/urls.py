from django.urls import path

from . import views

urlpatterns = [
    path('loans', views.loan_list, name='loan-list'),
    path('loans/<str:loan_id>', views.loan_detail),
    path('loans/<str:loan_id>/return', views.loan_return, name='loan-return'),
    path('ui/loans/new/', views.loan_lend_form, name='loan-lend-form'),
    path('ui/loans/', views.loan_catalog, name='loan-catalog'),
    path('ui/loans/<str:loan_id>/', views.loan_catalog_detail, name='loan-catalog-detail'),
    path('ui/loans/<str:loan_id>/return/', views.loan_catalog_return, name='loan-catalog-return'),
]
