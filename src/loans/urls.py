from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('loans', csrf_exempt(views.loan_list)),
    path('loans/<str:loan_id>/return', csrf_exempt(views.loan_return)),
    path('loans/<str:loan_id>', views.loan_detail),
    path('ui/loans/', views.loan_catalog),
    path('ui/loans/new/', views.loan_catalog_new),
    path('ui/loans/<str:loan_id>/return/', views.loan_catalog_return),
    path('ui/loans/<str:loan_id>/', views.loan_catalog_detail),
]
