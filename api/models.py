from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10, null=True, blank=True, unique=True)
    address = models.TextField()
    is_admin = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    hospital = models.ForeignKey('disease_monitor.Hospital', null=True, blank=True, on_delete=models.SET_NULL, related_name='users', help_text="Hospital this admin manages")
    
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        # Superusers have all permissions
        if self.is_superuser:
            return True
        
        # Check if user has the specific permission
        return super().has_perm(perm, obj)
    
    def has_module_perms(self, app_label):
        # Superusers have all module permissions
        if self.is_superuser:
            return True
        
        # Check if user has any permissions for the module
        return super().has_module_perms(app_label)
    
    def get_user_type(self):
        """Get the user type for display purposes"""
        if self.is_superuser:
            return "Superuser"
        elif self.is_admin:
            return "Admin"
        else:
            return "User"


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Automatically assign users to appropriate groups when created or updated
    """
    if created:
        # Import here to avoid circular imports
        from .utils import assign_user_to_group
        
        if instance.is_superuser:
            # Superusers don't need to be in specific groups
            pass
        elif instance.is_admin:
            # Assign to Admins group
            assign_user_to_group(instance, 'Admins')
        else:
            # Assign to Users group
            assign_user_to_group(instance, 'Users')
    else:
        # Handle updates to user permissions
        from .utils import assign_user_to_group, remove_user_from_group
        
        if instance.is_superuser:
            # Remove from all groups if superuser
            remove_user_from_group(instance, 'Users')
            remove_user_from_group(instance, 'Admins')
        elif instance.is_admin:
            # Ensure admin is in Admins group and not in Users group
            assign_user_to_group(instance, 'Admins')
            remove_user_from_group(instance, 'Users')
        else:
            # Ensure regular user is in Users group and not in Admins group
            assign_user_to_group(instance, 'Users')
            remove_user_from_group(instance, 'Admins')
    