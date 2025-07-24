#!/usr/bin/env python
"""
Script to test if the models are working correctly
"""

import pandas as pd
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import DiabetesData, MeningitisData, CholeraData, NationalHotspots, Disease, DiseaseYear
from src.models.disease_monitor import DiseaseMonitor

# Sample input (edit as needed)
input_data = {
    "age": 22,
    "sex": "Female",
    "pregnant_patient": False,
    "nhia_patient": True,
    "orgname": "Weija",
    "address_locality": "DANSOMAN",
    "disease_type": "malaria",
    "symptoms": [
        "Unexplained Weight Loss",
        "Fatigue",
        "Blurred Vision",
        "Frequent Infections"
    ],
    # "symptoms": ["Fever", "Headache", "Chills and Shivering", "Sweating", "Nausea and Vomiting"],
    "gemini_enabled": False
}

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

def test_model(input_data):
    disease_type = input_data["disease_type"].lower()
    model_dir = os.path.join("models", disease_type)
    monitor = DiseaseMonitor()
    monitor.load_models(path=model_dir)

    # Build DataFrame for prediction
    input_df = pd.DataFrame([{**input_data, 'symptoms': input_data['symptoms']}])
    X, _, feature_cols = monitor.preprocess_data(input_df, disease_type, training=False)
    model = monitor.models[disease_type]
    prediction = model.predict(X)[0]
    probability = float(model.predict_proba(X)[0][1])

    print(f"Disease type: {disease_type}")
    print(f"Feature columns: {feature_cols}")
    print(f"Feature values: {X.values.tolist()[0]}")
    print(f"Prediction: {prediction}")
    print(f"Probability: {probability}")

if __name__ == "__main__":
    # test_model_queries()
    # test_model_fields()
    # test_admin_queries()
    test_model(input_data) 