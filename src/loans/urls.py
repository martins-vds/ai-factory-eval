from django.urls import path

from . import views

urlpatterns = [
    path('loans', views.loan_list),
    path('loans/<str:loan_id>', views.loan_detail),
    path('ui/loans/', views.loan_catalog),
    path('ui/loans/new/', views.loan_catalog_new),
    path('ui/loans/<str:loan_id>/return/', views.loan_catalog_return),
    path('ui/loans/<str:loan_id>/', views.loan_catalog_detail),
    path('loans/<str:loan_id>/return', views.loan_return),
]
