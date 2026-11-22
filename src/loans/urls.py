from django.urls import path

from src.loans import views

urlpatterns = [
    path('loans', views.api_list),
    path('loans/<str:loan_id>', views.api_detail),
    path('ui/loans/', views.ui_list),
    path('ui/loans/<str:loan_id>/', views.ui_detail),
]
