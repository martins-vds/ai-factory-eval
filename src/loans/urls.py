from django.urls import path

from . import views

urlpatterns = [
    path('loans', views.catalog_list),
    path('loans/<str:loan_id>', views.catalog_item),
    path('ui/loans/', views.catalog_page),
    path('ui/loans/<str:loan_id>/', views.loan_page),
]
