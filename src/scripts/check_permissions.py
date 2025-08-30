#!/usr/bin/env python
"""
Script to check existing permissions in the database
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

def check_existing_permissions():
    """Check what permissions exist in the database"""
    
    print("Existing Permissions in Database")
    print("=" * 50)
    
    # Get all permissions
    permissions = Permission.objects.all().order_by('content_type__app_label', 'content_type__model', 'codename')
    
    current_app = None
    current_model = None
    
    for perm in permissions:
        app_label = perm.content_type.app_label
        model_name = perm.content_type.model
        codename = perm.codename
        name = perm.name
        
        # Print app header
        if current_app != app_label:
            current_app = app_label
            print(f"\nApp: {app_label}")
            print("-" * 30)
        
        # Print model header
        if current_model != model_name:
            current_model = model_name
            print(f"\n  Model: {model_name}")
        
        print(f"    {codename:<25} -> {name}")
    
    print(f"\nTotal permissions: {permissions.count()}")

def check_groups_and_permissions():
    """Check groups and their permissions"""
    
    print("\n" + "=" * 50)
    print("Groups and Their Permissions")
    print("=" * 50)
    
    groups = Group.objects.all()
    
    for group in groups:
        print(f"\nGroup: {group.name}")
        print("-" * 20)
        
        permissions = group.permissions.all().order_by('content_type__app_label', 'codename')
        
        if permissions:
            for perm in permissions:
                print(f"  {perm.codename}")
        else:
            print("  No permissions assigned")
        
        print(f"  Total: {permissions.count()} permissions")

def verify_permission_naming():
    """Verify the permission naming convention"""
    
    print("\n" + "=" * 50)
    print("Permission Naming Verification")
    print("=" * 50)
    
    # Check specific models
    models_to_check = [
        ('disease_monitor', 'diabetesdata'),
        ('disease_monitor', 'meningitisdata'),
        ('disease_monitor', 'choleradata'),
        ('disease_monitor', 'nationalhotspots'),
        ('disease_monitor', 'disease'),
        ('disease_monitor', 'diseaseyear'),
        ('api', 'user')
    ]
    
    for app_label, model_name in models_to_check:
        print(f"\nChecking {app_label}.{model_name}:")
        
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
            permissions = Permission.objects.filter(content_type=ct)
            
            expected_codenames = [
                f'add_{model_name}',
                f'change_{model_name}',
                f'delete_{model_name}',
                f'view_{model_name}'
            ]
            
            actual_codenames = [p.codename for p in permissions]
            
            print(f"  Expected: {expected_codenames}")
            print(f"  Actual:   {actual_codenames}")
            
            missing = set(expected_codenames) - set(actual_codenames)
            if missing:
                print(f"  Missing:  {list(missing)}")
            else:
                print("  ✓ All expected permissions exist")
                
        except ContentType.DoesNotExist:
            print(f"  ✗ ContentType not found for {app_label}.{model_name}")

if __name__ == "__main__":
    check_existing_permissions()
    check_groups_and_permissions()
    verify_permission_naming() 