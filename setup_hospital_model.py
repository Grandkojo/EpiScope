#!/usr/bin/env python3
"""
Setup script for Hospital model
This script will create the Hospital table and seed it with initial data
"""
import os
import sys
import django
import sqlite3

# Add the project directory to Python path
sys.path.append('/home/grandkojo/Documents/GITHUB/EpiScope')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from django.db import connection
from disease_monitor.models import Hospital

def create_hospital_table():
    """Create the hospitals table manually"""
    print("Creating hospitals table...")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) UNIQUE NOT NULL,
                slug VARCHAR(255) UNIQUE NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hospitals_name ON hospitals(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hospitals_slug ON hospitals(slug)")
        
        print("✅ Hospitals table created successfully")

def seed_hospital_data():
    """Seed the Hospital model with Weija Hospital"""
    print("Seeding hospital data...")
    
    try:
        # Check if Weija Hospital already exists
        existing_hospital = Hospital.objects.filter(name='Weija Hospital').first()
        
        if existing_hospital:
            print(f"✅ Weija Hospital already exists: {existing_hospital.name} (slug: {existing_hospital.slug})")
            return existing_hospital
        
        # Create Weija Hospital
        hospital = Hospital.objects.create(
            name='Weija Hospital',
            slug='weija'
        )
        
        print(f"✅ Created Weija Hospital: {hospital.name} (slug: {hospital.slug})")
        return hospital
        
    except Exception as e:
        print(f"❌ Error seeding hospital data: {str(e)}")
        return None

def verify_hospital_data():
    """Verify the hospital data was created correctly"""
    print("Verifying hospital data...")
    
    try:
        # Get all hospitals
        hospitals = Hospital.objects.all()
        print(f"✅ Total hospitals in database: {hospitals.count()}")
        
        for hospital in hospitals:
            print(f"  - {hospital.name} (slug: {hospital.slug})")
        
        # Test get_by_slug
        weija = Hospital.get_by_slug('weija')
        if weija:
            print(f"✅ Found Weija Hospital by slug: {weija.name}")
        else:
            print("❌ Could not find Weija Hospital by slug")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying hospital data: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🏥 Setting up Hospital model...")
    print("=" * 50)
    
    # Step 1: Create table
    create_hospital_table()
    
    # Step 2: Seed data
    hospital = seed_hospital_data()
    
    if hospital:
        # Step 3: Verify data
        verify_hospital_data()
        
        print("\n" + "=" * 50)
        print("🎉 Hospital model setup completed successfully!")
        print(f"✅ Weija Hospital created with slug: 'weija'")
    else:
        print("\n" + "=" * 50)
        print("💥 Hospital model setup failed!")
        sys.exit(1)

if __name__ == '__main__':
    main() 