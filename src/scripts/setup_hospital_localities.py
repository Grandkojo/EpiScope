#!/usr/bin/env python3
"""
Comprehensive script to set up Hospital Localities system
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"   Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def main():
    """Main setup process"""
    print("🚀 Hospital Localities Setup Process")
    print("=" * 80)
    print("This script will:")
    print("1. Extract hospital localities from HospitalHealthData")
    print("2. Create and run migrations for HospitalLocalities model")
    print("3. Seed the database with extracted data")
    print("4. Test the API endpoints")
    print()
    
    # Step 1: Extract data from database
    print("📊 Step 1: Extracting Hospital Localities from Database")
    print("=" * 60)
    
    if not run_command("python extract_hospital_localities.py", "Extracting hospital localities"):
        print("❌ Failed to extract data. Exiting.")
        return False
    
    # Check if CSV was created
    if not os.path.exists('hospital_localities.csv'):
        print("❌ CSV file was not created. Exiting.")
        return False
    
    print(f"✅ CSV file created: hospital_localities.csv")
    
    # Step 2: Create migrations
    print("\n📝 Step 2: Creating Database Migrations")
    print("=" * 60)
    
    if not run_command("python manage.py makemigrations disease_monitor", "Creating migrations"):
        print("❌ Failed to create migrations. Exiting.")
        return False
    
    # Step 3: Run migrations
    print("\n🗄️  Step 3: Running Database Migrations")
    print("=" * 60)
    
    if not run_command("python manage.py migrate", "Running migrations"):
        print("❌ Failed to run migrations. Exiting.")
        return False
    
    # Step 4: Seed the database
    print("\n🌱 Step 4: Seeding Database with Hospital Localities")
    print("=" * 60)
    
    if not run_command("python manage.py seed_hospital_localities --clear", "Seeding database"):
        print("❌ Failed to seed database. Exiting.")
        return False
    
    # Step 5: Test the setup
    print("\n🧪 Step 5: Testing the Setup")
    print("=" * 60)
    
    # Test dry run first
    if not run_command("python manage.py seed_hospital_localities --dry-run", "Testing dry run"):
        print("⚠️  Dry run failed, but continuing...")
    
    # Test API endpoints (if server is running)
    print("\n🌐 Step 6: Testing API Endpoints")
    print("=" * 60)
    print("To test the API endpoints, start your Django server and run:")
    print("   python test_hospital_localities_api.py")
    
    # Step 7: Show usage examples
    print("\n📚 Step 7: Usage Examples")
    print("=" * 60)
    
    print("🎯 API Endpoints Available:")
    print("   GET /api/hospital-localities/")
    print("   GET /api/hospital-localities/stats/")
    print("   GET /api/hospital-localities/search/?q=query")
    print()
    
    print("🔧 Management Commands Available:")
    print("   python manage.py seed_hospital_localities")
    print("   python manage.py seed_hospital_localities --clear")
    print("   python manage.py seed_hospital_localities --dry-run")
    print()
    
    print("📊 Model Methods Available:")
    print("   HospitalLocalities.get_all_localities()")
    print("   HospitalLocalities.get_all_hospitals()")
    print("   HospitalLocalities.search_localities(query)")
    print("   HospitalLocalities.search_hospitals(query)")
    print("   HospitalLocalities.get_localities_for_hospital(orgname)")
    print("   HospitalLocalities.get_hospitals_for_locality(locality)")
    
    print("\n✅ Hospital Localities setup completed successfully!")
    print("🎉 You can now use the HospitalLocalities model and API endpoints.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 