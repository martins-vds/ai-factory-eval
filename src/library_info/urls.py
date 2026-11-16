from django.urls import path

from . import views

urlpatterns = [
    path('about', views.public_about),
    path('ui/about/', views.about_page),
]
