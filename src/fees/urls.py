from django.urls import path

from . import views

urlpatterns = [
    path('fees/<str:loan_id>', views.fee_api, name='fee-api'),
    path('payments/<str:loan_id>', views.payment_api, name='payment-api'),
    path('ui/fees/<str:loan_id>/', views.fee_page, name='fee-page'),
    path('ui/payments/<str:loan_id>/', views.payment_page, name='payment-page'),
]
