#!/usr/bin/env python3
"""
Test script for the new XGBoost models and updated DiseaseMonitor class.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.disease_monitor import DiseaseMonitor

def create_test_data():
    """Create test data for diabetes and malaria predictions"""
    
    # Test data for diabetes
    diabetes_test_data = pd.DataFrame({
        'Schedule Date': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'Locality': ['Weija', 'Kwashieman', 'Block Factory'],
        'Age': ['45 Year(s)', '62 Year(s)', '38 Year(s)'],
        'Gender': ['Male', 'Female', 'Male'],
        'Pregnant Patient': ['No', 'No', 'No'],
        'NHIA Patient': ['Insured', 'Insured', 'Insured'],
        'Medicine Prescribed': [
            'METFORMIN[ DIAMET | 500MG | Tablet | BID | For 120 Days ]',
            'INSULIN[ INSULIN | 100IU | Injection | Daily | For 30 Days ]',
            'PARACETAMOL[ PARACETAMOL | 500MG | Tablet | TDS | For 7 Days ]'
        ],
        'Principal Diagnosis': [
            'E1101 [Type 2 diabetes mellitus with hyperosmolarity with coma]',
            'E1102 [Type 2 diabetes mellitus with hyperosmolarity without coma]',
            'I10 [Essential (primary) hypertension]'
        ],
        'Additional Diagnosis': ['', '', ''],
        'Cost of Treatment (GHS )': [50, 75, 25]
    })
    
    # Test data for malaria
    malaria_test_data = pd.DataFrame({
        'Schedule Date': ['2024-01-15', '2024-01-16', '2024-01-17'],
        'Locality': ['Weija', 'Kwashieman', 'Block Factory'],
        'Age': ['25 Year(s)', '32 Year(s)', '18 Year(s)'],
        'Gender': ['Female', 'Male', 'Female'],
        'Pregnant Patient': ['No', 'No', 'Yes'],
        'NHIA Patient': ['Insured', 'Insured', 'Insured'],
        'Medicine Prescribed': [
            'ARTEMETHER+LUMEFANTRINE[ COARTEM | 20/120MG | Tablet | BID | For 3 Days ]',
            'QUININE[ QUININE | 600MG | Tablet | TDS | For 7 Days ]',
            'PARACETAMOL[ PARACETAMOL | 500MG | Tablet | TDS | For 7 Days ]'
        ],
        'Principal Diagnosis': [
            'B50.9 [Plasmodium falciparum malaria, unspecified]',
            'B54 [Unspecified malaria]',
            'I10 [Essential (primary) hypertension]'
        ],
        'Additional Diagnosis': ['', '', ''],
        'Cost of Treatment (GHS )': [30, 45, 20]
    })
    
    return diabetes_test_data, malaria_test_data

def test_model_loading():
    """Test loading the new XGBoost models"""
    print("🔍 Testing model loading...")
    
    monitor = DiseaseMonitor()
    
    # Try to load models from the models directory
    models_path = "src/artifacts/models"
    if os.path.exists(models_path):
        monitor.load_models(models_path)
        
        # Check if models were loaded
        if monitor.models:
            print("✅ Models loaded successfully!")
            for disease, model in monitor.models.items():
                print(f"   - {disease}: {type(model).__name__}")
                if hasattr(model, 'feature_importances_'):
                    print(f"     Features: {len(model.feature_importances_)}")
        else:
            print("❌ No models loaded")
            return False
    else:
        print(f"❌ Models directory not found: {models_path}")
        return False
    
    return True

def test_prediction_without_symptoms():
    """Test predictions without symptom analysis"""
    print("\n🔍 Testing predictions without symptoms...")
    
    monitor = DiseaseMonitor()
    models_path = "src/artifacts/models"
    monitor.load_models(models_path)
    
    diabetes_data, malaria_data = create_test_data()
    
    # Test diabetes prediction
    if 'diabetes' in monitor.models:
        print("\n📊 Testing diabetes prediction:")
        diabetes_results = monitor.predict_with_new_models(diabetes_data, 'diabetes')
        
        for i, result in enumerate(diabetes_results):
            print(f"   Patient {i+1}:")
            print(f"     Base probability: {result['base_probability']:.4f}")
            print(f"     Prediction: {result['prediction']}")
            print(f"     Locality: {result['locality']}")
            print(f"     Cost included: {result['cost_included']}")
    
    # Test malaria prediction
    if 'malaria' in monitor.models:
        print("\n📊 Testing malaria prediction:")
        malaria_results = monitor.predict_with_new_models(malaria_data, 'malaria')
        
        for i, result in enumerate(malaria_results):
            print(f"   Patient {i+1}:")
            print(f"     Base probability: {result['base_probability']:.4f}")
            print(f"     Prediction: {result['prediction']}")
            print(f"     Locality: {result['locality']}")
            print(f"     Cost included: {result['cost_included']}")
    
    return True

def test_prediction_with_symptoms():
    """Test predictions with symptom analysis (if Vertex AI is available)"""
    print("\n🔍 Testing predictions with symptoms...")
    
    # Initialize with a dummy project ID for testing
    monitor = DiseaseMonitor(project_id="test-project")
    models_path = "src/artifacts/models"
    monitor.load_models(models_path)
    
    diabetes_data, malaria_data = create_test_data()
    
    # Test symptoms for diabetes
    diabetes_symptoms = "Patient reports frequent urination, excessive thirst, and fatigue"
    
    if 'diabetes' in monitor.models:
        print("\n📊 Testing diabetes prediction with symptoms:")
        diabetes_results = monitor.predict_with_new_models(
            diabetes_data, 'diabetes', symptoms_text=diabetes_symptoms
        )
        
        for i, result in enumerate(diabetes_results):
            print(f"   Patient {i+1}:")
            print(f"     Base probability: {result['base_probability']:.4f}")
            if result.get('symptom_score') is not None:
                print(f"     Symptom score: {result['symptom_score']:.4f}")
                print(f"     Combined probability: {result['combined_probability']:.4f}")
                print(f"     Dynamic threshold: {result.get('dynamic_threshold', 'N/A')}")
            print(f"     Final prediction: {result['prediction']}")
    
    # Test symptoms for malaria
    malaria_symptoms = "Patient has high fever, chills, and headache"
    
    if 'malaria' in monitor.models:
        print("\n📊 Testing malaria prediction with symptoms:")
        malaria_results = monitor.predict_with_new_models(
            malaria_data, 'malaria', symptoms_text=malaria_symptoms
        )
        
        for i, result in enumerate(malaria_results):
            print(f"   Patient {i+1}:")
            print(f"     Base probability: {result['base_probability']:.4f}")
            if result.get('symptom_score') is not None:
                print(f"     Symptom score: {result['symptom_score']:.4f}")
                print(f"     Combined probability: {result['combined_probability']:.4f}")
                print(f"     Dynamic threshold: {result.get('dynamic_threshold', 'N/A')}")
            print(f"     Final prediction: {result['prediction']}")
    
    return True

def test_feature_engineering():
    """Test the feature engineering process"""
    print("\n🔍 Testing feature engineering...")
    
    monitor = DiseaseMonitor()
    diabetes_data, malaria_data = create_test_data()
    
    # Test feature engineering for diabetes
    print("\n📊 Testing diabetes feature engineering:")
    X_diabetes, _, features_diabetes = monitor.preprocess_data(diabetes_data, 'diabetes', training=False)
    print(f"   Features created: {len(features_diabetes)}")
    print(f"   Feature matrix shape: {X_diabetes.shape}")
    print(f"   Sample features: {features_diabetes[:5]}")
    
    # Test feature engineering for malaria
    print("\n📊 Testing malaria feature engineering:")
    X_malaria, _, features_malaria = monitor.preprocess_data(malaria_data, 'malaria', training=False)
    print(f"   Features created: {len(features_malaria)}")
    print(f"   Feature matrix shape: {X_malaria.shape}")
    print(f"   Sample features: {features_malaria[:5]}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing New XGBoost Models and DiseaseMonitor Updates")
    print("=" * 60)
    
    tests = [
        ("Model Loading", test_model_loading),
        ("Feature Engineering", test_feature_engineering),
        ("Prediction without Symptoms", test_prediction_without_symptoms),
        ("Prediction with Symptoms", test_prediction_with_symptoms)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The new models are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 