from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from .models import EmployeeProfile
from .decorators import admin_only, employee_required
from .forms import EmployeeCreateForm, EmployeeEditForm


@admin_only
def employee_list(request):
    """List all employees - admin only"""
    employees = EmployeeProfile.objects.select_related('user').all()
    context = {
        'employees': employees,
    }
    return render(request, 'employees/employee_list.html', context)


@admin_only
def employee_create(request):
    """Create new employee - admin only"""
    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Add to Employee group
            employee_group, _ = Group.objects.get_or_create(name='Employee')
            user.groups.add(employee_group)
            
            # Create/update employee profile
            profile, created = EmployeeProfile.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': form.cleaned_data['employee_id'],
                    'phone_number': form.cleaned_data['phone_number'],
                    'created_by': request.user
                }
            )
            
            if not created:
                profile.employee_id = form.cleaned_data['employee_id']
                profile.phone_number = form.cleaned_data['phone_number']
                profile.created_by = request.user
                profile.save()
            
            messages.success(request, f'Employee {user.username} created successfully!')
            return redirect('employee_list')
    else:
        # Generate next employee ID
        last_profile = EmployeeProfile.objects.all().order_by('id').last()
        if last_profile and last_profile.employee_id.startswith('EMP'):
            try:
                next_id = f"EMP{int(last_profile.employee_id[3:]) + 1:04d}"
            except:
                next_id = "EMP0001"
        else:
            next_id = "EMP0001"
        
        form = EmployeeCreateForm(initial={'employee_id': next_id})
    
    context = {
        'form': form,
    }
    return render(request, 'employees/employee_form.html', context)


@admin_only
def employee_edit(request, pk):
    """Edit employee - admin only"""
    profile = get_object_or_404(EmployeeProfile, pk=pk)
    user = profile.user
    
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=profile)
        if form.is_valid():
            # Update user fields
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Update profile
            form.save()
            
            messages.success(request, f'Employee {user.username} updated successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeEditForm(
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
    return render(request, 'employees/employee_form.html', context)


@admin_only
def employee_toggle_active(request, pk):
    """Toggle employee active status - admin only"""
    if request.method == 'POST':
        profile = get_object_or_404(EmployeeProfile, pk=pk)
        profile.is_active = not profile.is_active
        profile.save()
        
        status = 'activated' if profile.is_active else 'deactivated'
        messages.success(request, f'Employee {profile.user.username} {status} successfully!')
    
    return redirect('employee_list')


@employee_required
def employee_profile(request):
    """View employee's own profile"""
    profile, created = EmployeeProfile.objects.get_or_create(
        user=request.user,
        defaults={'employee_id': 'TEMP'}
    )
    
    if created:
        # Generate proper employee ID
        last_profile = EmployeeProfile.objects.exclude(pk=profile.pk).order_by('id').last()
        if last_profile and last_profile.employee_id.startswith('EMP'):
            try:
                profile.employee_id = f"EMP{int(last_profile.employee_id[3:]) + 1:04d}"
            except:
                profile.employee_id = "EMP0001"
        else:
            profile.employee_id = "EMP0001"
        profile.save()
    
    context = {
        'profile': profile,
    }
    return render(request, 'employees/profile.html', context)
