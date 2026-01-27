from django.urls import path
from . import views

urlpatterns = [
    path('', views.public_display, name='public_display'),
]
