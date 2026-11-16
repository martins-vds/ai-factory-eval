from django.urls import path

from . import views

urlpatterns = [
    path('about', views.about_page),
    path('ui/about/', views.about_ui_page),
]
