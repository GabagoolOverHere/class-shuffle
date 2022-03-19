from django.urls import path

from . import views

urlpatterns = [
    path('', views.shuffle, name='shuffle'),
]