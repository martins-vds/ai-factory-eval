from django.urls import path
from django.views.decorators.http import require_POST

from . import views

urlpatterns = [
    path('fees/<str:loan_id>', views.fee_detail),
    path('payments/<str:loan_id>', require_POST(views.payment)),
    path('ui/fees/<str:loan_id>/', views.fee_page),
    path('ui/payments/<str:loan_id>/', require_POST(views.payment_page)),
]
