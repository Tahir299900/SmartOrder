from django.shortcuts import render
from orders.models import Order


def public_display(request):
    # Get orders that are preparing or ready
    preparing_orders = Order.objects.filter(status='PREPARING').order_by('started_at')
    ready_orders = Order.objects.filter(status='READY').order_by('ready_at')
    
    return render(request, 'display/public_display.html', {
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders
    })
