from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    customer_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_customers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.customer_id})"

    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.user.is_superuser or self.user.groups.filter(name='Admin').exists()


# Signal to create/update customer profile
@receiver(post_save, sender=User)
def create_or_update_customer_profile(sender, instance, created, **kwargs):
    """Auto-create customer profile for non-superuser users"""
    if created and not instance.is_superuser:
        # Check if profile doesn't exist
        if not hasattr(instance, 'customer_profile'):
            # Generate customer ID
            last_profile = CustomerProfile.objects.all().order_by('id').last()
            if last_profile:
                cus_id = f"CUS{int(last_profile.customer_id[3:]) + 1:04d}"
            else:
                cus_id = "CUS0001"
            
            CustomerProfile.objects.create(
                user=instance,
                customer_id=cus_id
            )
