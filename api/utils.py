from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


def assign_user_to_group(user, group_name):
    """
    Assign a user to a specific group.
    
    Args:
        user: User instance
        group_name: Name of the group ('Users', 'Admins')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return True
    except Group.DoesNotExist:
        return False


def remove_user_from_group(user, group_name):
    """
    Remove a user from a specific group.
    
    Args:
        user: User instance
        group_name: Name of the group ('Users', 'Admins')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        group = Group.objects.get(name=group_name)
        user.groups.remove(group)
        return True
    except Group.DoesNotExist:
        return False


def get_user_groups(user):
    """
    Get all groups that a user belongs to.
    
    Args:
        user: User instance
    
    Returns:
        QuerySet: Groups the user belongs to
    """
    return user.groups.all()


def is_user_in_group(user, group_name):
    """
    Check if a user belongs to a specific group.
    
    Args:
        user: User instance
        group_name: Name of the group
    
    Returns:
        bool: True if user is in group, False otherwise
    """
    return user.groups.filter(name=group_name).exists()


def get_users_in_group(group_name):
    """
    Get all users in a specific group.
    
    Args:
        group_name: Name of the group
    
    Returns:
        QuerySet: Users in the group
    """
    try:
        group = Group.objects.get(name=group_name)
        return group.user_set.all()
    except Group.DoesNotExist:
        return User.objects.none()


def promote_user_to_admin(user):
    """
    Promote a user to admin status.
    
    Args:
        user: User instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user.is_admin = True
        user.save()
        assign_user_to_group(user, 'Admins')
        return True
    except Exception:
        return False


def demote_admin_to_user(user):
    """
    Demote an admin to regular user status.
    
    Args:
        user: User instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user.is_admin = False
        user.save()
        remove_user_from_group(user, 'Admins')
        assign_user_to_group(user, 'Users')
        return True
    except Exception:
        return False


def get_user_permission_summary(user):
    """
    Get a summary of user permissions and groups.
    
    Args:
        user: User instance
    
    Returns:
        dict: Summary of user permissions
    """
    groups = get_user_groups(user)
    permissions = user.get_all_permissions()
    
    return {
        'username': user.username,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'is_admin': user.is_admin,
        'is_staff': user.is_staff,
        'groups': [group.name for group in groups],
        'permissions': list(permissions),
        'total_permissions': len(permissions)
    }


def create_default_user_groups():
    """
    Create default user groups if they don't exist.
    
    Returns:
        dict: Status of group creation
    """
    groups_created = {}
    
    # Create Users group
    users_group, created = Group.objects.get_or_create(name='Users')
    groups_created['Users'] = created
    
    # Create Admins group
    admins_group, created = Group.objects.get_or_create(name='Admins')
    groups_created['Admins'] = created
    
    return groups_created 