from django.urls import path
from . import views

urlpatterns = [
    path('', views.kitchen_display, name='kitchen_display'),
]
