# EpiScope Permission System Guide

## Overview

The EpiScope disease monitoring system implements a three-tier permission structure:

1. **Regular Users** - Read-only access to disease data and analytics
2. **Admins** - Manage disease metadata and configurations
3. **Superusers** - Full system access and management

## Permission Structure

### 1. Regular Users (Users Group)

**Model Level Permissions:**
- `view_diabetesdata`
- `view_meningitisdata`
- `view_choleradata`
- `view_nationalhotspots`
- `view_disease`
- `view_diseaseyear`

**View Level Access:**
- Dashboard data (read-only)
- Disease statistics and trends
- National hotspots data (filtered/aggregated)
- Available regions and filter options
- Own profile management

**Object Level Restrictions:**
- Can only view public disease data
- Cannot access raw database tables (managed=False models)
- Cannot modify any disease data

### 2. Admins (Admins Group)

**Model Level Permissions:**
- All user permissions PLUS:
- `add_disease`, `change_disease`, `delete_disease`
- `add_diseaseyear`, `change_diseaseyear`, `delete_diseaseyear`
- `view_user` (limited user management)

**View Level Access:**
- All user permissions PLUS:
- Disease definition management
- Disease year configuration management
- Basic user profile viewing
- Enhanced analytics access
- Data export capabilities

**Object Level Access:**
- Can manage disease metadata
- Can configure disease year settings
- Limited user data access (view only)

### 3. Superusers (Django Superuser)

**Model Level Permissions:**
- All permissions on all models
- Full database access including managed=False models
- Complete user management capabilities

**View Level Access:**
- Django admin interface access
- All API endpoints
- Database management
- System configuration

**Object Level Access:**
- Full CRUD on all objects
- Access to raw database tables
- User creation, modification, deletion

## Implementation Files

### 1. Admin Configuration (`disease_monitor/admin.py`)
- Custom admin classes for each model
- Permission-based access control
- Read-only fields for sensitive data
- Custom admin site branding

### 2. Permission Classes (`api/permissions.py`)
- `DashboardPermission` - Dashboard access
- `DiseaseManagementPermission` - Disease metadata management
- `UserManagementPermission` - User profile management
- `HotspotsPermission` - National hotspots access
- `IsAdminUser` - Admin-only access
- `IsSuperUser` - Superuser-only access

### 3. Utility Functions (`api/utils.py`)
- Group management functions
- User promotion/demotion utilities
- Permission summary generation
- Default group creation

### 4. User Model (`api/models.py`)
- Custom User model with admin flag
- Automatic group assignment
- Enhanced permission methods
- User type classification

## Setup Instructions

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Set Up Permission Groups
```bash
python manage.py setup_permissions
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Create Admin Users
```python
# In Django shell or management command
from api.models import User
from api.utils import promote_user_to_admin

# Create admin user
user = User.objects.create_user(
    username='admin_user',
    email='admin@example.com',
    password='secure_password',
    is_admin=True
)
```

## Usage Examples

### Managing User Permissions

```python
from api.utils import promote_user_to_admin, demote_admin_to_user, get_user_permission_summary

# Promote user to admin
user = User.objects.get(username='john_doe')
promote_user_to_admin(user)

# Demote admin to user
admin_user = User.objects.get(username='admin_user')
demote_admin_to_user(admin_user)

# Get permission summary
summary = get_user_permission_summary(user)
print(summary)
```

### Checking Permissions in Views

```python
from api.permissions import IsAdminUser, IsSuperUser

class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]
    
class SuperUserOnlyView(APIView):
    permission_classes = [IsSuperUser]
```

### Group Management

```python
from api.utils import assign_user_to_group, get_users_in_group

# Assign user to group
assign_user_to_group(user, 'Admins')

# Get all users in a group
admin_users = get_users_in_group('Admins')
```

## API Endpoint Permissions

| Endpoint | Method | Users | Admins | Superusers |
|----------|--------|-------|--------|------------|
| `/api/register/` | POST | ✓ | ✓ | ✓ |
| `/api/profile/` | GET/PUT | ✓ (own) | ✓ (own) | ✓ (all) |
| `/api/dashboard/` | GET | ✓ | ✓ | ✓ |
| `/api/diseases/` | GET | ✓ | ✓ | ✓ |
| `/api/diseases/` | POST/PUT/DELETE | ✗ | ✓ | ✓ |
| `/api/hotspots/` | GET | ✓ | ✓ | ✓ |
| `/api/hotspots/` | POST/PUT/DELETE | ✗ | ✗ | ✓ |
| `/api/regions/` | GET | ✓ | ✓ | ✓ |

## Security Considerations

### 1. Data Protection
- Raw disease data tables are read-only for all users
- Only superusers can modify historical data
- User data is protected by object-level permissions

### 2. API Security
- All endpoints require authentication (except registration)
- JWT tokens with 25-minute expiration
- Automatic token refresh mechanism

### 3. Admin Interface
- Custom permission checks in admin classes
- Read-only fields for sensitive data
- Group-based access control

## Monitoring and Auditing

### 1. Permission Logging
```python
from api.utils import get_user_permission_summary
import logging

logger = logging.getLogger(__name__)

def log_user_access(user, action):
    summary = get_user_permission_summary(user)
    logger.info(f"User {user.username} ({summary['groups']}) performed {action}")
```

### 2. Group Membership Tracking
```python
from django.contrib.auth.models import Group

def get_group_statistics():
    stats = {}
    for group in Group.objects.all():
        stats[group.name] = group.user_set.count()
    return stats
```

## Troubleshooting

### Common Issues

1. **User not getting correct permissions**
   - Check if user is in correct group
   - Verify `is_admin` flag is set correctly
   - Run `setup_permissions` command

2. **Admin interface access denied**
   - Ensure user has `is_staff=True`
   - Check group membership
   - Verify model permissions

3. **API endpoint access denied**
   - Check authentication token
   - Verify permission classes
   - Check user group membership

### Debug Commands

```python
# Check user permissions
python manage.py shell
>>> from api.models import User
>>> user = User.objects.get(username='test_user')
>>> from api.utils import get_user_permission_summary
>>> print(get_user_permission_summary(user))

# Check group permissions
>>> from django.contrib.auth.models import Group
>>> group = Group.objects.get(name='Admins')
>>> print([p.codename for p in group.permissions.all()])
```

## Future Enhancements

### 1. Role-Based Permissions
- Custom roles with specific permission sets
- Dynamic permission assignment
- Role inheritance

### 2. Audit Trail
- Permission change logging
- Access attempt tracking
- Data modification history

### 3. Advanced Security
- IP-based access restrictions
- Time-based permissions
- Multi-factor authentication integration

## Maintenance

### Regular Tasks

1. **Permission Audits**
   - Monthly review of user permissions
   - Clean up unused permissions
   - Verify group assignments

2. **Security Updates**
   - Update permission classes as needed
   - Review admin interface access
   - Monitor access patterns

3. **User Management**
   - Regular user account reviews
   - Admin privilege audits
   - Inactive user cleanup

This permission system provides a solid foundation for your disease monitoring application while maintaining security and scalability for future growth. 