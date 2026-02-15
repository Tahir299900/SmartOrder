from django.urls import path
from . import views

urlpatterns = [
    # Admin only - Customer management
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:pk>/toggle-active/', views.customer_toggle_active, name='customer_toggle_active'),
    
    # Customers - Own profile
    path('profile/', views.customer_profile, name='customer_profile'),
]
