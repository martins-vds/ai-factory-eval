from django.urls import path

from . import views

urlpatterns = [
    path('loans', views.loan_list),
    path('loans/<str:loan_id>', views.loan_detail),
    path('loans/<str:loan_id>/return', views.loan_return),
    path('ui/loans/new/', views.loan_lend_page),
    path('ui/loans/', views.loan_catalog),
    path('ui/loans/<str:loan_id>/', views.loan_catalog_detail),
    path('ui/loans/<str:loan_id>/return/', views.loan_return_page),
]
