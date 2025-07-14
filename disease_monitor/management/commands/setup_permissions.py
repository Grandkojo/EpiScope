from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from disease_monitor.models import DiabetesData, MeningitisData, CholeraData, NationalHotspots, Disease, DiseaseYear, RegionPopulation
from api.models import User


class Command(BaseCommand):
    help = 'Set up permission groups for EpiScope disease monitoring system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up permission groups...')
        
        # Get content types
        diabetes_ct = ContentType.objects.get_for_model(DiabetesData)
        meningitis_ct = ContentType.objects.get_for_model(MeningitisData)
        cholera_ct = ContentType.objects.get_for_model(CholeraData)
        hotspots_ct = ContentType.objects.get_for_model(NationalHotspots)
        disease_ct = ContentType.objects.get_for_model(Disease)
        disease_year_ct = ContentType.objects.get_for_model(DiseaseYear)
        region_population_ct = ContentType.objects.get_for_model(RegionPopulation)
        user_ct = ContentType.objects.get_for_model(User)
        
        # Create or get groups
        users_group, created = Group.objects.get_or_create(name='Users')
        admins_group, created = Group.objects.get_or_create(name='Admins')
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created group: Users'))
        if created:
            self.stdout.write(self.style.SUCCESS('Created group: Admins'))
        
        # Clear existing permissions
        users_group.permissions.clear()
        admins_group.permissions.clear()
        
        # Permissions for Users group (read-only access to disease data)
        user_permissions = [
            # View permissions for disease data
            Permission.objects.get(content_type=diabetes_ct, codename='view_diabetesdata'),
            Permission.objects.get(content_type=meningitis_ct, codename='view_meningitisdata'),
            Permission.objects.get(content_type=cholera_ct, codename='view_choleradata'),
            Permission.objects.get(content_type=hotspots_ct, codename='view_nationalhotspots'),
            Permission.objects.get(content_type=disease_ct, codename='view_disease'),
            Permission.objects.get(content_type=disease_year_ct, codename='view_diseaseyear'),
            Permission.objects.get(content_type=region_population_ct, codename='view_regionpopulation'),
        ]
        
        users_group.permissions.add(*user_permissions)
        self.stdout.write(self.style.SUCCESS(f'Added {len(user_permissions)} permissions to Users group'))
        
        # Permissions for Admins group (manage disease metadata and configurations)
        admin_permissions = user_permissions + [
            # Disease management
            Permission.objects.get(content_type=disease_ct, codename='add_disease'),
            Permission.objects.get(content_type=disease_ct, codename='change_disease'),
            Permission.objects.get(content_type=disease_ct, codename='delete_disease'),
            
            # Disease year management
            Permission.objects.get(content_type=disease_year_ct, codename='add_diseaseyear'),
            Permission.objects.get(content_type=disease_year_ct, codename='change_diseaseyear'),
            Permission.objects.get(content_type=disease_year_ct, codename='delete_diseaseyear'),
            
            # Region population management
            Permission.objects.get(content_type=region_population_ct, codename='add_regionpopulation'),
            Permission.objects.get(content_type=region_population_ct, codename='change_regionpopulation'),
            Permission.objects.get(content_type=region_population_ct, codename='delete_regionpopulation'),
            
            # Limited user management (view only)
            Permission.objects.get(content_type=user_ct, codename='view_user'),
        ]
        
        admins_group.permissions.add(*admin_permissions)
        self.stdout.write(self.style.SUCCESS(f'Added {len(admin_permissions)} permissions to Admins group'))
        
        # Superuser permissions are handled by Django's built-in is_superuser flag
        # They automatically get all permissions
        
        self.stdout.write(self.style.SUCCESS('Permission setup completed successfully!'))
        self.stdout.write('\nPermission Summary:')
        self.stdout.write('==================')
        self.stdout.write('Users Group:')
        self.stdout.write('  - View disease data (read-only)')
        self.stdout.write('  - Access dashboard and analytics')
        self.stdout.write('  - View national hotspots')
        self.stdout.write('  - View regional population data')
        self.stdout.write('  - Update own profile')
        self.stdout.write('\nAdmins Group:')
        self.stdout.write('  - All user permissions')
        self.stdout.write('  - Manage disease definitions')
        self.stdout.write('  - Manage disease year configurations')
        self.stdout.write('  - Manage regional population data')
        self.stdout.write('  - View user profiles (limited)')
        self.stdout.write('\nSuperuser:')
        self.stdout.write('  - Full access to all models and data')
        self.stdout.write('  - Database management')
        self.stdout.write('  - User management')
        self.stdout.write('  - System configuration') 