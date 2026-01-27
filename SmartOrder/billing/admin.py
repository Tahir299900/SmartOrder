from django.contrib import admin
from .models import Bill, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['order', 'subtotal', 'tax_amount', 'total_amount', 'created_at']
    readonly_fields = ['subtotal', 'tax_amount', 'total_amount']
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['bill', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['payment_method', 'status']
