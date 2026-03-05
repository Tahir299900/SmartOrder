import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Order, OrderItem
from menu.models import MenuItem, Category
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import stripe
import boto3
from django.contrib import messages
from django.http import JsonResponse
from .lambda_utils import invoke_lambda  # Import the function we wrote above

# Initialize Stripe with your secret key
stripe.api_key = ''; 


# Create Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')  # Use the region where your Lambda is deployed


def create_order_and_process_payment(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        stripe_token = request.POST.get('stripe_token', None)
        
        customer_name = request.POST.get('customer_name')
        notes = request.POST.get('notes')

        # Create the order in the database
        order = Order.objects.create(
            customer_name=customer_name,
            notes=notes,
            status='Pending'
        )
        
        # If 'Card' is selected, process payment through Stripe
        if payment_method == 'card' and stripe_token:
            try:
                intent = stripe.PaymentIntent.create(
                    amount=5000,  # Amount in cents (for example, $50)
                    currency='usd',
                    payment_method=stripe_token,
                    confirmation_method='manual',
                    confirm=True
                )

                if intent.status == 'succeeded':
                    order.status = 'Paid'
                    order.save()

                    return JsonResponse({'success': True, 'order_id': order.id})
                else:
                    return JsonResponse({'error': 'Payment failed'}, status=400)

            except stripe.error.CardError as e:
                return JsonResponse({'error': str(e)}, status=400)

        elif payment_method == 'cash':
            # For Cash payment, just mark order as 'Cash Pending'
            order.status = 'Cash Pending'
            order.save()

            return JsonResponse({'success': True, 'order_id': order.id})

        else:
            return JsonResponse({'error': 'Invalid payment method'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def create_order(request):
    categories = Category.objects.all()
    menu_items = MenuItem.objects.filter(is_available=True)
    
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '')
        notes = request.POST.get('notes', '')
        
        order = Order.objects.create(
            customer_name=customer_name,
            notes=notes,
            created_by=request.user
        )
        
        # Add order items
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                menu_item_id = key.split('_')[1]
                quantity = int(value)
                if quantity > 0:
                    menu_item = MenuItem.objects.get(id=menu_item_id)
                    special_instructions = request.POST.get(f'instructions_{menu_item_id}', '')
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity,
                        special_instructions=special_instructions
                    )
        
        # Send real-time update to kitchen and display
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'kitchen',
            {
                'type': 'order_update',
                'data': {
                    'action': 'new_order',
                    'order_id': order.id,
                    'order_number': order.order_number
                }
            }
        )

        # Check if the customer_name is empty or null, and set a default name
        customer_name = order.customer_name or "Unknown Customer"  # Default name if empty or None

        # Prepare the event data to send to Lambda (ensure these match the expected parameters)
        event_data = {
            "recipient_email": "tahirhussainse90@gmail.com",
            "customer_name": customer_name,
            "order_number": order.order_number 
        }

        try:
            # Invoke the Lambda function
            response = lambda_client.invoke(
                FunctionName='SendEmailFromSES',  # Your Lambda function name
                InvocationType='RequestResponse',  # 'Event' for async invocation
                Payload=json.dumps(event_data)  # Pass the event data to Lambda
            )

            # Read the response from Lambda
            result = response['Payload'].read().decode('utf-8')

        except Exception as e:
            return JsonResponse({"error": str(e)})
        
        return redirect('order_success', order_id=order.id)
    
    return render(request, 'orders/create_order.html', {
        'categories': categories,
        'menu_items': menu_items
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            
            # Update timestamps
            if new_status == 'PREPARING' and not order.started_at:
                order.started_at = timezone.now()
            elif new_status == 'READY' and not order.ready_at:
                order.ready_at = timezone.now()
            elif new_status == 'COMPLETED' and not order.completed_at:
                order.completed_at = timezone.now()
            
            order.save()
            
            # Send real-time update
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'kitchen',
                {
                    'type': 'order_update',
                    'data': {
                        'action': 'status_update',
                        'order_id': order.id,
                        'order_number': order.order_number,
                        'status': order.status
                    }
                }
            )
            async_to_sync(channel_layer.group_send)(
                'display',
                {
                    'type': 'order_update',
                    'data': {
                        'action': 'status_update',
                        'order_id': order.id,
                        'order_number': order.order_number,
                        'status': order.status
                    }
                }
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'status': order.status})
        
        return redirect('order_detail', order_id=order_id)
    
    return JsonResponse({'success': False}, status=400)
