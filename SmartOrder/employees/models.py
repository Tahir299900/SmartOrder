from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_employees'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.employee_id})"

    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.user.is_superuser or self.user.groups.filter(name='Admin').exists()


# Signal to create/update employee profile
@receiver(post_save, sender=User)
def create_or_update_employee_profile(sender, instance, created, **kwargs):
    """Auto-create employee profile for non-superuser users"""
    if created and not instance.is_superuser:
        # Check if profile doesn't exist
        if not hasattr(instance, 'employee_profile'):
            # Generate employee ID
            last_profile = EmployeeProfile.objects.all().order_by('id').last()
            if last_profile:
                emp_id = f"EMP{int(last_profile.employee_id[3:]) + 1:04d}"
            else:
                emp_id = "EMP0001"
            
            EmployeeProfile.objects.create(
                user=instance,
                employee_id=emp_id
            )
