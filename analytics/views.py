from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q, F, DecimalField
from django.db.models import ExpressionWrapper
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta, datetime
from employees.decorators import admin_only
from orders.models import Order, OrderItem
from menu.models import MenuItem


@admin_only
def reports_dashboard(request):
    """Main reports dashboard"""
    # Get date range from request or default to last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Parse date filters if provided
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d')
        start_date = timezone.make_aware(start_date)
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d')
        end_date = timezone.make_aware(end_date.replace(hour=23, minute=59, second=59))
    
    # Basic statistics
    total_orders = Order.objects.filter(created_at__range=[start_date, end_date]).count()
    completed_orders = Order.objects.filter(
        status='COMPLETED',
        created_at__range=[start_date, end_date]
    ).count()
    cancelled_orders = Order.objects.filter(
        status='CANCELLED',
        created_at__range=[start_date, end_date]
    ).count()
    
    # Revenue calculation (sum of all order items)
    total_revenue = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__range=[start_date, end_date]
    ).aggregate(
        total=Sum(ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField()))
    )['total'] or 0
    
    # Average order value
    completed_order_ids = Order.objects.filter(
        status='COMPLETED',
        created_at__range=[start_date, end_date]
    ).values_list('id', flat=True)
    
    if completed_order_ids:
        avg_order_value = total_revenue / len(completed_order_ids)
    else:
        avg_order_value = 0
    
    # Orders by status
    orders_by_status = Order.objects.filter(
        created_at__range=[start_date, end_date]
    ).values('status').annotate(count=Count('id')).order_by('-count')
    
    # Daily order trends
    daily_orders = Order.objects.filter(
        created_at__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Calculate revenue for each day
    daily_orders_list = list(daily_orders)
    for day in daily_orders_list:
        day_revenue = OrderItem.objects.filter(
            order__status='COMPLETED',
            order__created_at__date=day['date']
        ).aggregate(
            total=Sum(ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField()))
        )['total'] or 0
        day['revenue'] = day_revenue
    
    # Top selling items
    top_items = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__range=[start_date, end_date]
    ).annotate(
        item_revenue=ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField())
    ).values(
        'menu_item__name'
    ).annotate(
        quantity=Sum('quantity'),
        revenue=Sum('item_revenue')
    ).order_by('-quantity')[:10]
    
    # Peak hours
    peak_hours = Order.objects.filter(
        created_at__range=[start_date, end_date]
    ).annotate(
        hour=TruncHour('created_at')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'orders_by_status': orders_by_status,
        'daily_orders': daily_orders_list,
        'top_items': top_items,
        'peak_hours': peak_hours,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@admin_only
def sales_report(request):
    """Detailed sales report"""
    # Get period from request (today, week, month, custom)
    period = request.GET.get('period', 'month')
    end_date = timezone.now()
    
    if period == 'today':
        start_date = end_date.replace(hour=0, minute=0, second=0)
    elif period == 'week':
        start_date = end_date - timedelta(days=7)
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
    elif period == 'custom':
        start_date = datetime.strptime(request.GET.get('start_date', ''), '%Y-%m-%d')
        end_date = datetime.strptime(request.GET.get('end_date', ''), '%Y-%m-%d')
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date.replace(hour=23, minute=59, second=59))
    else:
        start_date = end_date - timedelta(days=30)
    
    # Sales by date
    sales_by_date = Order.objects.filter(
        status='COMPLETED',
        created_at__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total_orders=Count('id')
    ).order_by('date')
    
    # Calculate revenue for each date
    sales_data = []
    total_orders = 0
    total_revenue = 0
    
    for item in sales_by_date:
        date_revenue = OrderItem.objects.filter(
            order__status='COMPLETED',
            order__created_at__date=item['date']
        ).aggregate(
            total=Sum(ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField()))
        )['total'] or 0
        
        avg_per_order = (date_revenue / item['total_orders']) if item['total_orders'] > 0 else 0
        
        sales_data.append({
            'date': item['date'],
            'total_orders': item['total_orders'],
            'total_revenue': date_revenue,
            'avg_per_order': avg_per_order
        })
        total_orders += item['total_orders']
        total_revenue += date_revenue
    
    avg_revenue_per_order = (total_revenue / total_orders) if total_orders > 0 else 0
    
    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'sales_data': sales_data,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_revenue_per_order': avg_revenue_per_order,
    }
    
    return render(request, 'analytics/sales_report.html', context)


@admin_only
def menu_performance(request):
    """Menu items performance report"""
    # Get date range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Menu items performance
    items_performance = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__range=[start_date, end_date]
    ).annotate(
        item_revenue=ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField())
    ).values(
        'menu_item__id',
        'menu_item__name',
        'menu_item__category__name',
        'menu_item__price'
    ).annotate(
        times_ordered=Count('id'),
        total_quantity=Sum('quantity'),
        total_revenue=Sum('item_revenue')
    ).order_by('-total_revenue')
    
    # Calculate percentage contribution
    total_revenue = sum(item['total_revenue'] or 0 for item in items_performance)
    for item in items_performance:
        item['revenue_percentage'] = (item['total_revenue'] / total_revenue * 100) if total_revenue > 0 else 0
    
    # Category performance
    category_performance = OrderItem.objects.filter(
        order__status='COMPLETED',
        order__created_at__range=[start_date, end_date]
    ).annotate(
        item_revenue=ExpressionWrapper(F('quantity') * F('unit_price'), output_field=DecimalField())
    ).values(
        'menu_item__category__name'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('item_revenue')
    ).order_by('-total_revenue')
    
    context = {
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'items_performance': items_performance,
        'category_performance': category_performance,
        'total_revenue': total_revenue,
    }
    
    return render(request, 'analytics/menu_performance.html', context)


@admin_only
def order_analytics(request):
    """Order completion and timing analytics"""
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Orders statistics
    orders = Order.objects.filter(created_at__range=[start_date, end_date])
    
    total_orders = orders.count()
    completed = orders.filter(status='COMPLETED').count()
    cancelled = orders.filter(status='CANCELLED').count()
    
    # Completion rate
    completion_rate = (completed / total_orders * 100) if total_orders > 0 else 0
    
    # Average preparation time (for completed orders)
    completed_orders = orders.filter(status='COMPLETED', started_at__isnull=False, ready_at__isnull=False)
    
    prep_times = []
    for order in completed_orders:
        if order.started_at and order.ready_at:
            prep_time = (order.ready_at - order.started_at).total_seconds() / 60  # in minutes
            prep_times.append(prep_time)
    
    avg_prep_time = sum(prep_times) / len(prep_times) if prep_times else 0
    
    # Cancellation rate
    cancellation_rate = (cancelled / total_orders * 100) if total_orders > 0 else 0
    
    # Status breakdown
    status_breakdown = []
    for status in ['PENDING', 'PREPARING', 'READY', 'COMPLETED', 'CANCELLED']:
        count = orders.filter(status=status).count()
        percentage = (count / total_orders * 100) if total_orders > 0 else 0
        if count > 0:
            status_breakdown.append({
                'status': status,
                'count': count,
                'percentage': percentage
            })
    
    # Peak hours
    peak_hours = orders.annotate(
        hour=TruncHour('created_at')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Calculate peak hour percentages
    max_peak = peak_hours[0]['count'] if peak_hours else 1
    for peak in peak_hours:
        peak['percentage'] = (peak['count'] / max_peak * 100)
    
    # Daily trends
    daily_trends = orders.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='COMPLETED')),
        cancelled=Count('id', filter=Q(status='CANCELLED'))
    ).order_by('-date')[:14]
    
    # Calculate completion rate for each day
    for day in daily_trends:
        day['completion_rate'] = (day['completed'] / day['total'] * 100) if day['total'] > 0 else 0
    
    context = {
        'days': days,
        'start_date': start_date,
        'end_date': end_date,
        'total_orders': total_orders,
        'completed': completed,
        'cancelled': cancelled,
        'completion_rate': completion_rate,
        'cancellation_rate': cancellation_rate,
        'avg_prep_time': avg_prep_time,
        'status_breakdown': status_breakdown,
        'peak_hours': peak_hours,
        'daily_trends': daily_trends,
    }
    
    return render(request, 'analytics/order_analytics.html', context)
