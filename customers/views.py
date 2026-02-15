from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from .models import CustomerProfile
from .decorators import admin_only, customer_required
from .forms import CustomerCreateForm, CustomerEditForm


@admin_only
def customer_list(request):
    """List all customers - admin only"""
    customers = CustomerProfile.objects.select_related('user').all()
    context = {
        'customers': customers,
    }
    return render(request, 'customers/customer_list.html', context)

@admin_only
def customer_list(request):
    """List all customers - admin only"""
    customers = CustomerProfile.objects.select_related('user').all()
    context = {
        'customers': customers,
    }
    return render(request, 'customers/customer_list.html', context)

@admin_only
def customer_create(request):
    """Create new customer - admin only"""
    if request.method == 'POST':
        form = CustomerCreateForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Add to Customer group
            customer_group, _ = Group.objects.get_or_create(name='Customer')
            user.groups.add(customer_group)
            
            # Create/update customer profile
            profile, created = CustomerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'customer_id': form.cleaned_data['customer_id'],
                    'phone_number': form.cleaned_data['phone_number'],
                    'created_by': request.user
                }
            )
            
            if not created:
                profile.customer_id = form.cleaned_data['customer_id']
                profile.phone_number = form.cleaned_data['phone_number']
                profile.created_by = request.user
                profile.save()
            
            messages.success(request, f'Customer {user.username} created successfully!')
            return redirect('customer_list')
    else:
        # Generate next customer ID
        last_profile = CustomerProfile.objects.all().order_by('id').last()
        if last_profile and last_profile.customer_id.startswith('EMP'):
            try:
                next_id = f"EMP{int(last_profile.customer_id[3:]) + 1:04d}"
            except:
                next_id = "EMP0001"
        else:
            next_id = "EMP0001"
        
        form = CustomerCreateForm(initial={'customer_id': next_id})
    
    context = {
        'form': form,
    }
    return render(request, 'customers/customer_form.html', context)


@admin_only
def customer_edit(request, pk):
    """Edit customer - admin only"""
    profile = get_object_or_404(CustomerProfile, pk=pk)
    user = profile.user
    
    if request.method == 'POST':
        form = CustomerEditForm(request.POST, instance=profile)
        if form.is_valid():
            # Update user fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Update profile
            form.save()
            
            messages.success(request, f'Customer {user.username} updated successfully!')
            return redirect('customer_list')
    else:
        form = CustomerEditForm(
            instance=profile,
            initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
        )
    
    context = {
        'form': form,
        'profile': profile,
        'edit_mode': True,
    }
    return render(request, 'customers/customer_form.html', context)


@admin_only
def customer_toggle_active(request, pk):
    """Toggle customer active status - admin only"""
    if request.method == 'POST':
        profile = get_object_or_404(CustomerProfile, pk=pk)
        profile.is_active = not profile.is_active
        profile.save()
        
        status = 'activated' if profile.is_active else 'deactivated'
        messages.success(request, f'Customer {profile.user.username} {status} successfully!')
    
    return redirect('customer_list')


@customer_required
def customer_profile(request):
    """View customer's own profile"""
    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user,
        defaults={'customer_id': 'TEMP'}
    )
    
    if created:
        # Generate proper customer ID
        last_profile = CustomerProfile.objects.exclude(pk=profile.pk).order_by('id').last()
        if last_profile and last_profile.customer_id.startswith('EMP'):
            try:
                profile.customer_id = f"EMP{int(last_profile.customer_id[3:]) + 1:04d}"
            except:
                profile.customer_id = "EMP0001"
        else:
            profile.customer_id = "EMP0001"
        profile.save()
    
    context = {
        'profile': profile,
    }
    return render(request, 'customers/profile.html', context)
