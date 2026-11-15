from django.urls import path

from . import views

urlpatterns = [
    path('fees/<str:loan_id>', views.fee_detail),
    path('payments/<str:loan_id>', views.payment_detail),
    path('ui/fees/<str:loan_id>/', views.fee_page, name='fee-page'),
    path('ui/payments/<str:loan_id>/', views.payment_page),
]
