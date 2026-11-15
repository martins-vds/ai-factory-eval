from django.urls import path

from . import views

urlpatterns = [
    path('about', views.about, name='about'),
    path('ui/about/', views.about_page, name='about-page'),
]
