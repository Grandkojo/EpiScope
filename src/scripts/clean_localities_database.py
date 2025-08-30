#!/usr/bin/env python3
"""
Clean Localities Database Script
Cleans up existing localities and replaces with main localities
"""

import os
import sys
import django
import pandas as pd

# Setup Django
sys.path.append('/home/grandkojo/Documents/GITHUB/EpiScope')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import HospitalLocalities, HospitalHealthData
from django.db import connection

def clean_localities_database():
    """Clean up localities in the database"""
    print("Cleaning localities in database...")
    
    # First, let's see what we have
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM hospital_localities")
        total_localities = cursor.fetchone()[0]
        print(f"Current localities in database: {total_localities}")
        
        cursor.execute("SELECT locality, COUNT(*) FROM hospital_localities GROUP BY locality ORDER BY COUNT(*) DESC LIMIT 10")
        top_localities = cursor.fetchall()
        print("\nTop 10 current localities:")
        for locality, count in top_localities:
            print(f"  {locality}: {count}")
    
    # Clear existing localities
    print("\nClearing existing localities...")
    HospitalLocalities.objects.all().delete()
    print("Cleared all existing localities")
    
    # Load clean localities CSV
    if not os.path.exists('final_localities_for_db.csv'):
        print("Error: final_localities_for_db.csv not found. Run create_final_localities.py first.")
        return
    
    clean_localities_df = pd.read_csv('final_localities_for_db.csv')
    print(f"Loading {len(clean_localities_df)} final localities...")
    
    # Create new locality records
    new_localities = []
    for _, row in clean_localities_df.iterrows():
        new_localities.append(HospitalLocalities(
            locality=row['locality'],
            orgname=row['orgname']
        ))
    
    # Bulk insert
    HospitalLocalities.objects.bulk_create(new_localities)
    print(f"Inserted {len(new_localities)} final localities")
    
    # Verify
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM hospital_localities")
        new_total = cursor.fetchone()[0]
        print(f"New total localities: {new_total}")
        
        cursor.execute("SELECT locality FROM hospital_localities ORDER BY locality")
        all_localities = [row[0] for row in cursor.fetchall()]
        print(f"\nAll localities: {', '.join(all_localities)}")

def update_health_data_localities():
    """Update health data to use main localities"""
    print("\nUpdating health data localities...")
    
    # Load the mapping
    if not os.path.exists('final_locality_mapping.json'):
        print("Error: final_locality_mapping.json not found. Run create_final_localities.py first.")
        return
    
    import json
    with open('final_locality_mapping.json', 'r') as f:
        locality_mapping = json.load(f)
    
    print(f"Loaded mapping with {len(locality_mapping)} entries")
    
    # Update health data records
    updated_count = 0
    for record in HospitalHealthData.objects.all():
        original_locality = record.address_locality
        if original_locality in locality_mapping:
            new_locality = locality_mapping[original_locality]
            if new_locality != original_locality:
                record.address_locality = new_locality
                record.save()
                updated_count += 1
    
    print(f"Updated {updated_count} health data records with normalized localities")

def main():
    """Main process"""
    print("Starting locality database cleanup...")
    
    # Step 1: Clean localities table
    clean_localities_database()
    
    # Step 2: Update health data localities
    update_health_data_localities()
    
    print("\nLocality cleanup completed!")

if __name__ == "__main__":
    main() 