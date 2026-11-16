"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from src.loans import views

urlpatterns = [
    path('loans', views.loan_list, name='loan-list'),
    path('loans/<str:loan_id>', views.loan_detail, name='loan-detail'),
    path('ui/loans/', views.loan_catalog, name='loan-catalog'),
    path('ui/loans/<str:loan_id>/', views.loan_page, name='loan-page'),
]
