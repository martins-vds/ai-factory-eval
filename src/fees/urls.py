from django.urls import path

from . import views

urlpatterns = [
    path('fees/<str:loan_id>', views.fee_api),
    path('ui/fees/<str:loan_id>/', views.fee_page),
]
