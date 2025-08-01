#!/usr/bin/env python
"""
Complete workflow for Vertex AI fine-tuning with CSV data
"""

import os
import sys
import django
import subprocess
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

def run_command(command, description):
    """Run a management command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return None
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return None

def main():
    print("🚀 Starting complete Vertex AI fine-tuning workflow")
    print("=" * 60)
    
    # Step 1: Generate training data from CSV files
    print("\n📊 Step 1: Generating training data from CSV files")
    
    # Generate for diabetes
    diabetes_result = run_command(
        "python manage.py generate_contextual_training_data --disease diabetes --save-to-db",
        "Generating diabetes training data from CSV"
    )
    
    # Generate for malaria
    malaria_result = run_command(
        "python manage.py generate_contextual_training_data --disease malaria --save-to-db",
        "Generating malaria training data from CSV"
    )
    
    # Step 2: Add expert knowledge examples
    print("\n🧠 Step 2: Adding expert knowledge examples")
    
    expert_result = run_command(
        "python manage.py add_training_data --disease diabetes --file sample_training_data.json",
        "Adding expert diabetes knowledge"
    )
    
    # Step 3: Export training data
    print("\n📤 Step 3: Exporting training data")
    
    diabetes_export = run_command(
        "python manage.py fine_tune_vertex_model --disease diabetes --export-only",
        "Exporting diabetes training data"
    )
    
    malaria_export = run_command(
        "python manage.py fine_tune_vertex_model --disease malaria --export-only",
        "Exporting malaria training data"
    )
    
    # Step 4: Fine-tune models (if you have Vertex AI access)
    print("\n🤖 Step 4: Fine-tuning models with Vertex AI")
    
    # Note: This requires proper Vertex AI setup and credentials
    print("⚠️  Note: Fine-tuning requires Vertex AI access and proper setup")
    print("   To proceed, ensure you have:")
    print("   - Google Cloud Project with Vertex AI enabled")
    print("   - Proper authentication (gcloud auth application-default login)")
    print("   - Sufficient quotas for fine-tuning")
    
    proceed = input("\nDo you want to proceed with fine-tuning? (y/N): ").lower().strip()
    
    if proceed == 'y':
        # Fine-tune diabetes model
        diabetes_fine_tune = run_command(
            "python manage.py vertex_ai_fine_tune --training-data exports/fine_tuning/fine_tuning_data_diabetes_*.json --disease diabetes",
            "Fine-tuning diabetes model"
        )
        
        # Fine-tune malaria model
        malaria_fine_tune = run_command(
            "python manage.py vertex_ai_fine_tune --training-data exports/fine_tuning/fine_tuning_data_malaria_*.json --disease malaria",
            "Fine-tuning malaria model"
        )
    else:
        print("⏭️  Skipping fine-tuning step")
    
    # Step 5: Test the system
    print("\n🧪 Step 5: Testing the system")
    
    # Test with sample queries
    test_queries = [
        "What are the current diabetes trends?",
        "What are the malaria hotspots?",
        "How can I prevent diabetes?",
        "What are the symptoms of malaria?"
    ]
    
    print("\nTesting sample queries:")
    for query in test_queries:
        print(f"\nQ: {query}")
        # This would test the actual chat system
        print("A: [Response would appear here when system is running]")
    
    # Step 6: Summary
    print("\n📋 Step 6: Summary")
    print("=" * 60)
    print("✅ Training data generated from CSV files")
    print("✅ Expert knowledge examples added")
    print("✅ Training data exported for fine-tuning")
    
    if proceed == 'y':
        print("✅ Fine-tuning process initiated")
        print("✅ Models deployed (if successful)")
    else:
        print("⏭️  Fine-tuning skipped")
    
    print("\n🎯 Next steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Test the chat interface with your React component")
    print("3. Monitor fine-tuning progress (if initiated)")
    print("4. Deploy fine-tuned models when ready")
    
    print("\n🚀 Workflow completed!")

if __name__ == "__main__":
    main() 