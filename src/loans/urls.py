from django.urls import path

from src.loans import ui_views, views

urlpatterns = [
    path('loans', views.loan_list_api),
    path('loans/<str:loan_id>', views.loan_detail_api),
    path('ui/loans/', ui_views.loan_catalog_page, name='loan-catalog-page'),
    path('ui/loans/<str:loan_id>/', ui_views.loan_detail_page, name='loan-detail-page'),
]
