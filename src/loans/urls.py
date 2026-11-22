from django.urls import path

from . import views

urlpatterns = [
    path('loans', views.catalog_list, name='loan_list_api'),
    path('loans/<str:loan_id>', views.catalog_item, name='loan_detail_api'),
    path('ui/loans/', views.catalog_page, name='loan_catalog'),
    path('ui/loans/<str:loan_id>/', views.loan_page, name='loan_page'),
]
