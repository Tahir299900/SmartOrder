from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from employees.models import EmployeeProfile


class Command(BaseCommand):
    help = 'Set up user groups (Admin and Employee) and assign existing users'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, admin_created = Group.objects.get_or_create(name='Admin')
        employee_group, employee_created = Group.objects.get_or_create(name='Employee')

        if admin_created:
            self.stdout.write(self.style.SUCCESS('✓ Created "Admin" group'))
        else:
            self.stdout.write('✓ "Admin" group already exists')

        if employee_created:
            self.stdout.write(self.style.SUCCESS('✓ Created "Employee" group'))
        else:
            self.stdout.write('✓ "Employee" group already exists')

        # Assign superusers to Admin group
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            admin_group.user_set.add(user)
        
        if superusers.count() > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Assigned {superusers.count()} superuser(s) to Admin group')
            )

        # Assign non-superusers to Employee group
        regular_users = User.objects.filter(is_superuser=False)
        for user in regular_users:
            if not user.groups.filter(name='Admin').exists():
                employee_group.user_set.add(user)
                
                # Ensure they have employee profile
                if not hasattr(user, 'employee_profile'):
                    last_profile = EmployeeProfile.objects.all().order_by('id').last()
                    if last_profile and last_profile.employee_id.startswith('EMP'):
                        try:
                            emp_id = f"EMP{int(last_profile.employee_id[3:]) + 1:04d}"
                        except:
                            emp_id = "EMP0001"
                    else:
                        emp_id = "EMP0001"
                    
                    EmployeeProfile.objects.create(
                        user=user,
                        employee_id=emp_id
                    )
        
        if regular_users.count() > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Assigned {regular_users.count()} user(s) to Employee group')
            )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Group setup complete!')
        )
        self.stdout.write(f'  - Admin group: {admin_group.user_set.count()} users')
        self.stdout.write(f'  - Employee group: {employee_group.user_set.count()} users')
