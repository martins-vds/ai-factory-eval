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

from django.urls import include, path

from src.fees import views as fee_views

urlpatterns = [
    path('', include('src.loans.urls')),
    path('fees/<str:loan_id>', fee_views.fee_api),
    path('payments/<str:loan_id>', fee_views.payment_api),
    path('ui/fees/<str:loan_id>/', fee_views.fee_page, name='ui-fee-page'),
    path('ui/payments/<str:loan_id>/', fee_views.payment_page),
]
