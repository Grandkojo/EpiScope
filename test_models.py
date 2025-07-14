#!/usr/bin/env python
"""
Script to test if the models are working correctly
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import DiabetesData, MeningitisData, CholeraData, NationalHotspots, Disease, DiseaseYear

def test_model_queries():
    """Test if we can query the models without errors"""
    
    print("Testing Model Queries")
    print("=" * 40)
    
    models_to_test = [
        ('DiabetesData', DiabetesData),
        ('MeningitisData', MeningitisData),
        ('CholeraData', CholeraData),
        ('NationalHotspots', NationalHotspots),
        ('Disease', Disease),
        ('DiseaseYear', DiseaseYear)
    ]
    
    for model_name, model_class in models_to_test:
        print(f"\nTesting {model_name}:")
        try:
            # Try to get the first record
            first_record = model_class.objects.first()
            if first_record:
                print(f"  ✓ Success - Found {model_class.objects.count()} records")
                print(f"    First record: {first_record}")
            else:
                print(f"  ✓ Success - No records found (table exists)")
        except Exception as e:
            print(f"  ✗ Error: {e}")

def test_model_fields():
    """Test if we can access model fields"""
    
    print("\n" + "=" * 40)
    print("Testing Model Fields")
    print("=" * 40)
    
    # Test CholeraData specifically
    print("\nTesting CholeraData fields:")
    try:
        cholera = CholeraData.objects.first()
        if cholera:
            print(f"  periodname: {cholera.periodname}")
            print(f"  cholera_cases_cds: {cholera.cholera_cases_cds}")
            print(f"  cholera_deaths_cds: {cholera.cholera_deaths_cds}")
            print("  ✓ All fields accessible")
        else:
            print("  No cholera data found")
    except Exception as e:
        print(f"  ✗ Error accessing fields: {e}")

def test_admin_queries():
    """Test queries that the admin interface would make"""
    
    print("\n" + "=" * 40)
    print("Testing Admin-like Queries")
    print("=" * 40)
    
    try:
        # Test the query that was failing
        cholera_list = CholeraData.objects.all()[:10]  # Limit to 10 records
        print(f"✓ Successfully queried CholeraData - found {len(cholera_list)} records")
        
        for cholera in cholera_list:
            print(f"  - {cholera.periodname}: {cholera.cholera_cases_cds} cases, {cholera.cholera_deaths_cds} deaths")
            
    except Exception as e:
        print(f"✗ Error in admin-like query: {e}")

if __name__ == "__main__":
    test_model_queries()
    test_model_fields()
    test_admin_queries() 