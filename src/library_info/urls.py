from django.urls import path

from . import views

urlpatterns = [
    path('about', views.about_legacy),
    path('ui/about/', views.about_page),
]
