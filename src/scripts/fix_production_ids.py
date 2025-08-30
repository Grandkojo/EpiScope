#!/usr/bin/env python3
"""
Fix NULL ID issue in HospitalHealthData and HospitalLocalities tables
This script will properly set the auto-incrementing IDs for all records that currently have NULL IDs.
"""

import os
import sys
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import HospitalHealthData, HospitalLocalities

def fix_table_ids(table_name, model_class):
    """Fix NULL IDs in a specific table"""
    print(f"🔧 Fixing NULL IDs in {table_name} table...")
    
    with connection.cursor() as cursor:
        # First, let's check the current state
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE id IS NULL")
        null_count = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Current state for {table_name}:")
        print(f"   • Total records: {total_count}")
        print(f"   • Records with NULL IDs: {null_count}")
        
        if null_count == 0:
            print(f"✅ No NULL IDs found in {table_name}. Table is already correct.")
            return
        
        # Get column names dynamically
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND column_name != 'id'
            ORDER BY ordinal_position
        """)
        columns = [row[0] for row in cursor.fetchall()]
        columns_str = ', '.join(columns)
        
        # Create a temporary table with proper IDs
        print(f"🔄 Creating temporary table with proper IDs for {table_name}...")
        cursor.execute(f"""
            CREATE TABLE {table_name}_temp AS
            SELECT 
                ROW_NUMBER() OVER (ORDER BY {columns_str}) as id,
                {columns_str}
            FROM {table_name}
        """)
        
        # Drop the original table and rename the temp table
        print(f"🔄 Replacing original {table_name} table...")
        cursor.execute(f"DROP TABLE {table_name}")
        cursor.execute(f"ALTER TABLE {table_name}_temp RENAME TO {table_name}")
        
        # Set the primary key constraint
        cursor.execute(f"ALTER TABLE {table_name} ADD PRIMARY KEY (id)")
        
        # Get the maximum ID to set the sequence
        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
        max_id = cursor.fetchone()[0]
        
        # Create the sequence if it doesn't exist
        sequence_name = f"{table_name}_id_seq"
        print(f"🔄 Creating sequence for auto-incrementing IDs in {table_name}...")
        cursor.execute(f"""
            CREATE SEQUENCE IF NOT EXISTS {sequence_name} 
            START WITH {max_id + 1}
            INCREMENT BY 1
            NO MINVALUE
            NO MAXVALUE
            CACHE 1
        """)
        
        # Set the sequence as the default for the id column
        cursor.execute(f"""
            ALTER TABLE {table_name} 
            ALTER COLUMN id SET DEFAULT nextval('{sequence_name}')
        """)
        
        # Verify the fix
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE id IS NULL")
        new_null_count = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        new_total_count = cursor.fetchone()[0]
        
        print(f"✅ Fix completed for {table_name}:")
        print(f"   • Total records: {new_total_count}")
        print(f"   • Records with NULL IDs: {new_null_count}")
        print(f"   • Sequence created and set to start at: {max_id + 1}")
        
        if new_null_count == 0:
            print(f"🎉 All NULL IDs have been fixed in {table_name}!")
        else:
            print(f"⚠️  Some NULL IDs still remain in {table_name}. Manual intervention may be needed.")

def fix_null_ids():
    """Fix NULL IDs in both HospitalHealthData and HospitalLocalities tables"""
    print("🚀 Starting database ID fixes...")
    
    # Fix HospitalHealthData table
    fix_table_ids('disease_monitor_hospitalhealthdata', HospitalHealthData)
    
    # Fix HospitalLocalities table
    fix_table_ids('hospital_localities', HospitalLocalities)

def verify_analytics():
    """Verify that analytics queries now work correctly"""
    print("\n🔍 Verifying analytics functionality...")
    
    try:
        # Test HospitalHealthData queries
        print("Testing HospitalHealthData...")
        total_count = HospitalHealthData.objects.count()
        print(f"✅ Total records count: {total_count}")
        
        diabetes_count = HospitalHealthData.objects.filter(
            principal_diagnosis_new__icontains='diabetes'
        ).count()
        print(f"✅ Diabetes records count: {diabetes_count}")
        
        weija_count = HospitalHealthData.objects.filter(
            orgname__icontains='weija'
        ).count()
        print(f"✅ Weija records count: {weija_count}")
        
        from datetime import date
        data_2023 = HospitalHealthData.objects.filter(
            month__year=2023
        ).count()
        print(f"✅ 2023 records count: {data_2023}")
        
        # Test HospitalLocalities queries
        print("\nTesting HospitalLocalities...")
        localities_count = HospitalLocalities.objects.count()
        print(f"✅ Total localities count: {localities_count}")
        
        weija_localities = HospitalLocalities.objects.filter(
            orgname__icontains='weija'
        ).count()
        print(f"✅ Weija localities count: {weija_localities}")
        
        print("✅ Analytics verification completed successfully!")
        
    except Exception as e:
        print(f"❌ Analytics verification failed: {str(e)}")

def create_prevention_guide():
    """Create a guide to prevent this issue in the future"""
    print("\n📋 PREVENTION GUIDE - How to avoid NULL ID issues in the future:")
    print("=" * 70)
    print("""
1. ALWAYS USE DJANGO ORM FOR DATA INSERTION:
   ✅ Good: HospitalHealthData.objects.create(...)
   ✅ Good: HospitalHealthData.objects.bulk_create(...)
   ❌ Bad: Direct SQL INSERT without proper ID handling

2. WHEN USING BULK OPERATIONS:
   ✅ Good: Use Django's bulk_create with proper model instances
   ✅ Good: Let Django handle ID generation automatically
   ❌ Bad: Bypassing Django ORM with raw SQL

3. WHEN MIGRATING DATA:
   ✅ Good: Use Django management commands with proper model usage
   ✅ Good: Use Django's ORM methods for data transformation
   ❌ Bad: Direct database operations that bypass Django

4. FOR DATA IMPORT SCRIPTS:
   ✅ Good: Create proper model instances and use save() or bulk_create()
   ✅ Good: Use Django's transaction management
   ❌ Bad: Raw SQL INSERT statements

5. CHECKLIST BEFORE DEPLOYING:
   - [ ] All data insertion uses Django ORM
   - [ ] No direct SQL INSERT statements bypassing Django
   - [ ] Primary keys are properly configured in models
   - [ ] Auto-increment sequences are properly set up
   - [ ] Test data insertion in development first

6. IF YOU MUST USE RAW SQL:
   - Always include proper ID generation
   - Use sequences correctly
   - Test thoroughly in development
   - Consider using Django's raw() method instead
""")

if __name__ == "__main__":
    print("🚀 Starting comprehensive database ID fix...")
    
    try:
        fix_null_ids()
        verify_analytics()
        create_prevention_guide()
        print("\n🎉 Database fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during database fix: {str(e)}")
        sys.exit(1) 