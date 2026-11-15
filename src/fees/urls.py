from django.urls import path

from . import views

urlpatterns = [
    path('fees/<str:loan_id>', views.late_fee),
]
