#!/usr/bin/env python
"""
Script to demonstrate Django's automatic permission codename generation
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from disease_monitor.models import DiabetesData, MeningitisData, CholeraData, NationalHotspots, Disease, DiseaseYear
from api.models import User

def show_model_permissions():
    """Show how Django generates permissions for each model"""
    
    models = [
        ('DiabetesData', DiabetesData),
        ('MeningitisData', MeningitisData), 
        ('CholeraData', CholeraData),
        ('NationalHotspots', NationalHotspots),
        ('Disease', Disease),
        ('DiseaseYear', DiseaseYear),
        ('User', User)
    ]
    
    print("Django Permission Codename Generation")
    print("=" * 50)
    
    for model_name, model_class in models:
        print(f"\nModel: {model_name}")
        print("-" * 30)
        
        # Get content type
        ct = ContentType.objects.get_for_model(model_class)
        
        # Get all permissions for this model
        permissions = Permission.objects.filter(content_type=ct)
        
        for perm in permissions:
            print(f"  {perm.codename:<25} -> {perm.name}")
        
        print(f"  Total permissions: {permissions.count()}")

def explain_naming_convention():
    """Explain the naming convention"""
    
    print("\n" + "=" * 50)
    print("Django Permission Naming Convention")
    print("=" * 50)
    
    examples = [
        ("DiabetesData", "diabetesdata"),
        ("MeningitisData", "meningitisdata"),
        ("NationalHotspots", "nationalhotspots"),
        ("Disease", "disease"),
        ("User", "user")
    ]
    
    print("\nModel Name -> Permission Base:")
    for model_name, permission_base in examples:
        print(f"  {model_name:<20} -> {permission_base}")
    
    print("\nGenerated Permissions:")
    print("  add_<permission_base>")
    print("  change_<permission_base>") 
    print("  delete_<permission_base>")
    print("  view_<permission_base>")
    
    print("\nExample for DiabetesData:")
    print("  add_diabetesdata")
    print("  change_diabetesdata")
    print("  delete_diabetesdata")
    print("  view_diabetesdata")

if __name__ == "__main__":
    show_model_permissions()
    explain_naming_convention() 