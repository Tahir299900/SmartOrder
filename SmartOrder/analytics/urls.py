from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('sales/', views.sales_report, name='sales_report'),
    path('menu/', views.menu_performance, name='menu_performance'),
    path('orders/', views.order_analytics, name='order_analytics'),
]
