from django.urls import path
from . import views

urlpatterns = [
    # Admin only - Employee management
    path('', views.employee_list, name='employee_list'),
    path('customers', views.customer_list, name='customer_list'),
    path('create/', views.employee_create, name='employee_create'),
    path('<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('<int:pk>/toggle-active/', views.employee_toggle_active, name='employee_toggle_active'),
    
    # Employee - Own profile
    path('profile/', views.employee_profile, name='employee_profile'),
]
