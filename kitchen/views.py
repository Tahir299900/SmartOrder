from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order


@login_required
def kitchen_display(request):
    # Get orders that are pending, preparing, or ready
    pending_orders = Order.objects.filter(status='PENDING').order_by('created_at')
    preparing_orders = Order.objects.filter(status='PREPARING').order_by('started_at')
    ready_orders = Order.objects.filter(status='READY').order_by('ready_at')
    
    return render(request, 'kitchen/kitchen_display.html', {
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'ready_orders': ready_orders
    })
