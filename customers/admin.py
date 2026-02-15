from django.contrib import admin
from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'user', 'phone_number', 'hire_date', 'is_active', 'created_by']
    list_filter = ['is_active', 'hire_date']
    search_fields = ['customer_id', 'user__username', 'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'customer_id', 'phone_number', 'is_active')
        }),
        ('Dates', {
            'fields': ('hire_date', 'created_at', 'updated_at')
        }),
        ('Management', {
            'fields': ('created_by',)
        }),
    )
