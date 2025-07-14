from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from api.models import User
from api.utils import (
    promote_user_to_admin, 
    demote_admin_to_user, 
    get_user_permission_summary,
    get_users_in_group,
    assign_user_to_group,
    remove_user_from_group
)


class Command(BaseCommand):
    help = 'Manage users, permissions, and groups for EpiScope'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['list', 'promote', 'demote', 'check', 'groups', 'assign-group', 'remove-group'],
            help='Action to perform'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for user-specific actions'
        )
        parser.add_argument(
            '--group',
            type=str,
            choices=['Users', 'Admins'],
            help='Group name for group-specific actions'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for user creation'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'list':
            self.list_users()
        elif action == 'promote':
            self.promote_user(options)
        elif action == 'demote':
            self.demote_user(options)
        elif action == 'check':
            self.check_user_permissions(options)
        elif action == 'groups':
            self.list_groups()
        elif action == 'assign-group':
            self.assign_to_group(options)
        elif action == 'remove-group':
            self.remove_from_group(options)

    def list_users(self):
        """List all users with their roles and groups"""
        self.stdout.write('User List:')
        self.stdout.write('=' * 80)
        
        users = User.objects.all().order_by('username')
        
        for user in users:
            groups = [group.name for group in user.groups.all()]
            user_type = user.get_user_type()
            
            self.stdout.write(
                f"{user.username:<20} | {user.email:<30} | {user_type:<10} | Groups: {', '.join(groups)}"
            )
        
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total users: {users.count()}')

    def promote_user(self, options):
        """Promote a user to admin"""
        username = options['username']
        if not username:
            raise CommandError('--username is required for promote action')
        
        try:
            user = User.objects.get(username=username)
            if user.is_admin:
                self.stdout.write(self.style.WARNING(f'User {username} is already an admin'))
                return
            
            if promote_user_to_admin(user):
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully promoted {username} to admin')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to promote {username} to admin')
                )
        except User.DoesNotExist:
            raise CommandError(f'User {username} does not exist')

    def demote_user(self, options):
        """Demote an admin to regular user"""
        username = options['username']
        if not username:
            raise CommandError('--username is required for demote action')
        
        try:
            user = User.objects.get(username=username)
            if not user.is_admin:
                self.stdout.write(self.style.WARNING(f'User {username} is not an admin'))
                return
            
            if demote_admin_to_user(user):
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully demoted {username} to regular user')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to demote {username} to regular user')
                )
        except User.DoesNotExist:
            raise CommandError(f'User {username} does not exist')

    def check_user_permissions(self, options):
        """Check detailed permissions for a user"""
        username = options['username']
        if not username:
            raise CommandError('--username is required for check action')
        
        try:
            user = User.objects.get(username=username)
            summary = get_user_permission_summary(user)
            
            self.stdout.write(f'Permission Summary for {username}:')
            self.stdout.write('=' * 50)
            self.stdout.write(f'Email: {summary["email"]}')
            self.stdout.write(f'User Type: {user.get_user_type()}')
            self.stdout.write(f'Groups: {", ".join(summary["groups"])}')
            self.stdout.write(f'Total Permissions: {summary["total_permissions"]}')
            self.stdout.write('Permissions:')
            for perm in sorted(summary['permissions']):
                self.stdout.write(f'  - {perm}')
            
        except User.DoesNotExist:
            raise CommandError(f'User {username} does not exist')

    def list_groups(self):
        """List all groups with their members"""
        self.stdout.write('Group List:')
        self.stdout.write('=' * 50)
        
        groups = Group.objects.all().order_by('name')
        
        for group in groups:
            users = group.user_set.all()
            self.stdout.write(f'\n{group.name}:')
            self.stdout.write(f'  Members ({users.count()}):')
            
            for user in users:
                user_type = user.get_user_type()
                self.stdout.write(f'    - {user.username} ({user_type})')

    def assign_to_group(self, options):
        """Assign a user to a group"""
        username = options['username']
        group_name = options['group']
        
        if not username:
            raise CommandError('--username is required for assign-group action')
        if not group_name:
            raise CommandError('--group is required for assign-group action')
        
        try:
            user = User.objects.get(username=username)
            if assign_user_to_group(user, group_name):
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully assigned {username} to {group_name} group')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to assign {username} to {group_name} group')
                )
        except User.DoesNotExist:
            raise CommandError(f'User {username} does not exist')

    def remove_from_group(self, options):
        """Remove a user from a group"""
        username = options['username']
        group_name = options['group']
        
        if not username:
            raise CommandError('--username is required for remove-group action')
        if not group_name:
            raise CommandError('--group is required for remove-group action')
        
        try:
            user = User.objects.get(username=username)
            if remove_user_from_group(user, group_name):
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully removed {username} from {group_name} group')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to remove {username} from {group_name} group')
                )
        except User.DoesNotExist:
            raise CommandError(f'User {username} does not exist') 