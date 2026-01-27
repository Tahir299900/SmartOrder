from django.contrib import admin
from .models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'phone_number', 'hire_date', 'is_active', 'created_by']
    list_filter = ['is_active', 'hire_date']
    search_fields = ['employee_id', 'user__username', 'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('user', 'employee_id', 'phone_number', 'is_active')
        }),
        ('Dates', {
            'fields': ('hire_date', 'created_at', 'updated_at')
        }),
        ('Management', {
            'fields': ('created_by',)
        }),
    )
