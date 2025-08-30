#!/usr/bin/env python3
"""
Reinforcement Learning Demo Script

This script demonstrates how to use the reinforcement learning system
with prediction history data for XGBoost model training.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import PredictionHistory
from disease_monitor.prediction_service import (
    PredictionHistoryService,
    ReinforcementLearningService
)
from reinforcement_xgboost_training import ReinforcementXGBoostTrainer


def create_sample_predictions():
    """Create sample prediction history data for demonstration"""
    print("📝 Creating sample prediction history data...")
    
    # Sample data for diabetes predictions
    diabetes_samples = [
        {
            'age': 45,
            'gender': 'Male',
            'locality': 'Weija',
            'schedule_date': datetime.now().date() - timedelta(days=5),
            'pregnant_patient': False,
            'nhia_patient': False,
            'vertex_ai_enabled': True,
            'disease_type': 'diabetes',
            'symptoms_description': 'Patient reports frequent urination, excessive thirst, and fatigue',
            'predicted_disease': 'Type 2 Diabetes',
            'confidence_score': 0.897,
            'status': 'confirmed',
            'actual_disease': 'Type 2 Diabetes',
            'medicine_prescribed': 'METFORMIN[ DIAMET | 500MG | Tablet | BID | For 120 Days ]',
            'cost_of_treatment': Decimal('50.00'),
            'hospital_name': 'Weija General Hospital'
        },
        {
            'age': 62,
            'gender': 'Female',
            'locality': 'Weija',
            'schedule_date': datetime.now().date() - timedelta(days=3),
            'pregnant_patient': False,
            'nhia_patient': True,
            'vertex_ai_enabled': True,
            'disease_type': 'diabetes',
            'symptoms_description': 'Patient reports weight loss, increased appetite, and blurred vision',
            'predicted_disease': 'Type 2 Diabetes',
            'confidence_score': 0.925,
            'status': 'confirmed',
            'actual_disease': 'Type 2 Diabetes',
            'medicine_prescribed': 'GLIBENCLAMIDE[ GLIBENCLAMIDE | 5MG | Tablet | OD | For 90 Days ]',
            'cost_of_treatment': Decimal('35.00'),
            'hospital_name': 'Weija General Hospital'
        },
        {
            'age': 38,
            'gender': 'Male',
            'locality': 'Weija',
            'schedule_date': datetime.now().date() - timedelta(days=2),
            'pregnant_patient': False,
            'nhia_patient': False,
            'vertex_ai_enabled': True,
            'disease_type': 'diabetes',
            'symptoms_description': 'Patient reports fatigue and slow-healing wounds',
            'predicted_disease': 'Type 2 Diabetes',
            'confidence_score': 0.789,
            'status': 'corrected',
            'actual_disease': 'Hypertension',
            'medicine_prescribed': 'AMLODIPINE[ AMLODIPINE | 10MG | Tablet | OD | For 30 Days ]',
            'cost_of_treatment': Decimal('25.00'),
            'hospital_name': 'Weija General Hospital'
        }
    ]
    
    # Sample data for malaria predictions
    malaria_samples = [
        {
            'age': 25,
            'gender': 'Female',
            'locality': 'Weija',
            'schedule_date': datetime.now().date() - timedelta(days=4),
            'pregnant_patient': True,
            'nhia_patient': False,
            'vertex_ai_enabled': True,
            'disease_type': 'malaria',
            'symptoms_description': 'Patient reports fever, headache, and body aches',
            'predicted_disease': 'Malaria',
            'confidence_score': 0.873,
            'status': 'confirmed',
            'actual_disease': 'Malaria',
            'medicine_prescribed': 'ARTEMETHER+LUMEFANTRINE[ COARTEM | 20/120MG | Tablet | BID | For 3 Days ]',
            'cost_of_treatment': Decimal('15.00'),
            'hospital_name': 'Weija General Hospital'
        },
        {
            'age': 12,
            'gender': 'Male',
            'locality': 'Weija',
            'schedule_date': datetime.now().date() - timedelta(days=1),
            'pregnant_patient': False,
            'nhia_patient': True,
            'vertex_ai_enabled': True,
            'disease_type': 'malaria',
            'symptoms_description': 'Patient reports high fever and chills',
            'predicted_disease': 'Malaria',
            'confidence_score': 0.912,
            'status': 'confirmed',
            'actual_disease': 'Malaria',
            'medicine_prescribed': 'ARTESUNATE[ ARTESUNATE | 60MG | Injection | STAT | Single Dose ]',
            'cost_of_treatment': Decimal('45.00'),
            'hospital_name': 'Weija General Hospital'
        }
    ]
    
    # Create predictions (you'll need to create a user first)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Get or create a demo user
    demo_user, created = User.objects.get_or_create(
        username='demo_user',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    
    created_count = 0
    
    # Create diabetes predictions
    for sample in diabetes_samples:
        try:
            prediction = PredictionHistoryService.create_prediction(
                user=demo_user,
                **sample
            )
            created_count += 1
        except Exception as e:
            print(f"Error creating diabetes prediction: {e}")
    
    # Create malaria predictions
    for sample in malaria_samples:
        try:
            prediction = PredictionHistoryService.create_prediction(
                user=demo_user,
                **sample
            )
            created_count += 1
        except Exception as e:
            print(f"Error creating malaria prediction: {e}")
    
    print(f"✅ Created {created_count} sample predictions")
    return created_count


def demonstrate_reinforcement_learning():
    """Demonstrate the reinforcement learning system"""
    print("\n🎯 Demonstrating Reinforcement Learning System")
    print("=" * 60)
    
    # 1. Show prediction history statistics
    print("\n📊 Prediction History Statistics:")
    stats = ReinforcementLearningService.get_learning_statistics(days_back=30)
    
    print(f"Total predictions: {stats['total_predictions']}")
    print(f"Pending predictions: {stats['pending_predictions']}")
    print(f"Confirmed predictions: {stats['confirmed_predictions']}")
    print(f"Corrected predictions: {stats['corrected_predictions']}")
    print(f"Discarded predictions: {stats['discarded_predictions']}")
    print(f"Learning ready predictions: {stats['learning_ready_predictions']}")
    print(f"Average confidence score: {stats['avg_confidence_score']:.3f}")
    print(f"Average learning score: {stats['avg_learning_score']:.3f}")
    print(f"Processing rate: {stats['processing_rate']:.1f}%")
    print(f"Success rate: {stats['success_rate']:.1f}%")
    
    # 2. Show recent training sessions
    print(f"\n📈 Recent Training Sessions:")
    for session in stats['recent_training_sessions']:
        print(f"  - {session['session_name']} ({session['disease_type']}) - {session['status']}")
        if session['test_accuracy']:
            print(f"    Test Accuracy: {session['test_accuracy']:.3f}")
    
    # 3. Demonstrate data aggregation
    print(f"\n📋 Data Aggregation Example:")
    period_start = datetime.now().date() - timedelta(days=7)
    period_end = datetime.now().date()
    
    aggregated_data = ReinforcementLearningService.aggregate_learning_data(
        period_start=period_start,
        period_end=period_end
    )
    
    print(f"Period: {period_start} to {period_end}")
    print(f"Total predictions: {aggregated_data['total_predictions']}")
    print(f"Confirmed predictions: {aggregated_data['confirmed_predictions']}")
    print(f"Corrected predictions: {aggregated_data['corrected_predictions']}")
    print(f"Model accuracy: {aggregated_data['model_accuracy']:.3f}")
    print(f"Model precision: {aggregated_data['model_precision']:.3f}")
    print(f"Model recall: {aggregated_data['model_recall']:.3f}")
    print(f"Model F1 score: {aggregated_data['model_f1_score']:.3f}")
    
    # 4. Show common medicines
    if aggregated_data['common_medicines']:
        print(f"\n💊 Common Medicines:")
        for medicine in aggregated_data['common_medicines'][:5]:
            frequency = aggregated_data['medicine_frequency'].get(medicine, 0)
            print(f"  - {medicine}: {frequency} times")


def demonstrate_xgboost_training():
    """Demonstrate XGBoost training with reinforcement learning"""
    print("\n🤖 Demonstrating XGBoost Training with Reinforcement Learning")
    print("=" * 60)
    
    # Check if we have enough data
    learning_ready_count = PredictionHistory.objects.filter(
        is_learning_ready=True
    ).count()
    
    if learning_ready_count < 5:
        print("⚠️ Not enough reinforcement learning data available")
        print("Need at least 5 learning-ready predictions to demonstrate training")
        return False
    
    # Demonstrate diabetes training
    print("\n🎯 Diabetes Model Training:")
    diabetes_trainer = ReinforcementXGBoostTrainer(
        disease_type='diabetes',
        base_model_path="src/artifacts/models/diabetes_xgboost_model_v2.pkl"
    )
    
    # Get reinforcement data
    reinforcement_data = diabetes_trainer.get_reinforcement_data(
        period_days=30,
        min_confidence=0.7
    )
    
    if not reinforcement_data.empty:
        print(f"📊 Found {len(reinforcement_data)} reinforcement learning records")
        print(f"📊 Data shape: {reinforcement_data.shape}")
        print(f"📊 Features: {list(reinforcement_data.columns)}")
        
        # Show sample data
        print(f"\n📋 Sample Reinforcement Data:")
        print(reinforcement_data[['age_numeric', 'is_male', 'target', 'weight', 'confidence_score']].head())
        
        # Note: Full training would require base data files
        print(f"\n💡 To run full training, use:")
        print(f"python manage.py run_reinforcement_training --disease-type diabetes")
        
    else:
        print("❌ No reinforcement learning data available for diabetes")
    
    return True


def main():
    """Main demonstration function"""
    print("🚀 Reinforcement Learning System Demonstration")
    print("=" * 60)
    
    # 1. Create sample data
    sample_count = create_sample_predictions()
    
    if sample_count == 0:
        print("❌ No sample data created. Check if demo user exists.")
        return
    
    # 2. Demonstrate reinforcement learning system
    demonstrate_reinforcement_learning()
    
    # 3. Demonstrate XGBoost training
    training_demo = demonstrate_xgboost_training()
    
    # Summary
    print("\n" + "=" * 60)
    print("DEMONSTRATION SUMMARY")
    print("=" * 60)
    
    print(f"✅ Created {sample_count} sample predictions")
    print("✅ Demonstrated reinforcement learning statistics")
    print("✅ Demonstrated data aggregation")
    
    if training_demo:
        print("✅ Demonstrated XGBoost training preparation")
    else:
        print("⚠️ XGBoost training demo skipped (insufficient data)")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Create more predictions with actual outcomes")
    print(f"2. Run: python manage.py run_reinforcement_training --disease-type both")
    print(f"3. Monitor model performance improvements")
    print(f"4. View SHAP plots in src/artifacts/reinforcement_shap_plots/")


if __name__ == "__main__":
    main() 