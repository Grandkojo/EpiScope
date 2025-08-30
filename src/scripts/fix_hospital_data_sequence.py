#!/usr/bin/env python3
"""
Fix HospitalHealthData table sequence issue
This script will create the missing sequence and properly configure the ID column for auto-incrementing.
"""

import os
import sys
import django
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import HospitalHealthData

def fix_hospital_health_data_sequence():
    """Fix the missing sequence for HospitalHealthData table"""
    print("🔧 Fixing HospitalHealthData table sequence...")
    
    with connection.cursor() as cursor:
        # Check current table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'disease_monitor_hospitalhealthdata' 
            AND column_name = 'id'
        """)
        id_column = cursor.fetchone()
        
        if not id_column:
            print("❌ ID column not found in disease_monitor_hospitalhealthdata table")
            return False
        
        print(f"📊 Current ID column: {id_column}")
        
        # Check if sequence exists
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_name = 'disease_monitor_hospitalhealthdata_id_seq'
        """)
        sequence_exists = cursor.fetchone()
        
        if sequence_exists:
            print("✅ Sequence already exists")
        else:
            print("🔄 Creating sequence for disease_monitor_hospitalhealthdata...")
            
            # Get the maximum ID to set the sequence start value
            cursor.execute("SELECT MAX(id) FROM disease_monitor_hospitalhealthdata")
            max_id_result = cursor.fetchone()
            max_id = max_id_result[0] if max_id_result[0] is not None else 0
            
            # Create the sequence
            cursor.execute(f"""
                CREATE SEQUENCE disease_monitor_hospitalhealthdata_id_seq 
                START WITH {max_id + 1}
                INCREMENT BY 1
                NO MINVALUE
                NO MAXVALUE
                CACHE 1
            """)
            
            print(f"✅ Created sequence starting at {max_id + 1}")
        
        # Set the sequence as the default for the id column
        print("🔄 Setting sequence as default for ID column...")
        cursor.execute("""
            ALTER TABLE disease_monitor_hospitalhealthdata 
            ALTER COLUMN id SET DEFAULT nextval('disease_monitor_hospitalhealthdata_id_seq')
        """)
        
        # Make sure the ID column is NOT NULL
        cursor.execute("""
            ALTER TABLE disease_monitor_hospitalhealthdata 
            ALTER COLUMN id SET NOT NULL
        """)
        
        # Set the sequence as owned by the table
        cursor.execute("""
            ALTER SEQUENCE disease_monitor_hospitalhealthdata_id_seq OWNED BY disease_monitor_hospitalhealthdata.id
        """)
        
        print("✅ Sequence configuration completed")
        
        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata WHERE id IS NULL")
        null_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM disease_monitor_hospitalhealthdata")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Verification:")
        print(f"   • Total records: {total_count}")
        print(f"   • Records with NULL IDs: {null_count}")
        
        if null_count == 0:
            print("🎉 HospitalHealthData table is now properly configured!")
            return True
        else:
            print("⚠️  Some NULL IDs still remain. Manual intervention may be needed.")
            return False

def test_bulk_create():
    """Test if bulk_create now works properly"""
    print("\n🧪 Testing bulk_create functionality...")
    
    try:
        # Create a test record
        test_record = HospitalHealthData(
            orgname='Test Hospital',
            address_locality='Test Locality',
            age=30,
            sex='Male',
            principal_diagnosis_new='Test Diagnosis',
            additional_diagnosis_new='',
            pregnant_patient=False,
            nhia_patient=False,
            month='2024-01-01',
            data_source='test'
        )
        
        # Test single create
        test_record.save()
        print(f"✅ Single record created with ID: {test_record.id}")
        
        # Test bulk create
        test_records = [
            HospitalHealthData(
                orgname='Test Hospital 2',
                address_locality='Test Locality 2',
                age=25,
                sex='Female',
                principal_diagnosis_new='Test Diagnosis 2',
                additional_diagnosis_new='',
                pregnant_patient=False,
                nhia_patient=True,
                month='2024-01-02',
                data_source='test'
            ),
            HospitalHealthData(
                orgname='Test Hospital 3',
                address_locality='Test Locality 3',
                age=40,
                sex='Male',
                principal_diagnosis_new='Test Diagnosis 3',
                additional_diagnosis_new='',
                pregnant_patient=False,
                nhia_patient=False,
                month='2024-01-03',
                data_source='test'
            )
        ]
        
        created_records = HospitalHealthData.objects.bulk_create(test_records)
        print(f"✅ Bulk create successful: {len(created_records)} records created")
        
        for record in created_records:
            print(f"   • Record ID: {record.id}")
        
        # Clean up test records
        HospitalHealthData.objects.filter(data_source='test').delete()
        print("🧹 Test records cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting HospitalHealthData sequence fix...")
    
    try:
        # Fix the sequence
        if fix_hospital_health_data_sequence():
            # Test the fix
            if test_bulk_create():
                print("\n🎉 All fixes completed successfully!")
                print("✅ You can now run the update_hospital_data command")
            else:
                print("\n⚠️  Sequence fix completed but bulk_create test failed")
        else:
            print("\n❌ Sequence fix failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error during fix: {str(e)}")
        sys.exit(1) 