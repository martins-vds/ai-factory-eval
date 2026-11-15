from django.urls import path

from src.loans import views


urlpatterns = [
    path('loans', views.loan_list, name='loan-list'),
]
