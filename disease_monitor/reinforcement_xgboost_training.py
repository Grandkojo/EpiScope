#!/usr/bin/env python3
"""
Reinforcement Learning Enhanced XGBoost Training

This module extends the XGBoost training process to incorporate reinforcement learning
data from prediction history, allowing the model to learn from actual outcomes and
treatment patterns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import re
import pickle
import os
import json
from pathlib import Path
from decimal import Decimal

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
from sklearn.feature_selection import SelectKBest, f_classif
import xgboost as xgb

# SHAP for model interpretability
import shap

# Django imports for database access
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'episcope.settings')
django.setup()

from disease_monitor.models import PredictionHistory, ReinforcementLearningData, ModelTrainingSession
from disease_monitor.prediction_service import ReinforcementLearningService

warnings.filterwarnings('ignore')
np.random.seed(42)

# Define medication dictionaries (same as in data_preprocessing_v2.py)
DIABETES_MEDICATIONS = [
    'metformin', 'insulin', 'glibenclamide', 'pioglitazone', 'glimeperide',
    'gliclazide', 'sitagliptin', 'linagliptin', 'empagliflozin', 'dapagliflozin',
    'canagliflozin', 'acarbose', 'miglitol', 'repaglinide', 'nateglinide'
]

MALARIA_MEDICATIONS = [
    'artemether', 'lumefantrine', 'artesunate', 'coartem', 'lonart',
    'artemether+lumefantrine', 'artemether+lumefan', 'artesunate injection',
    'artemether injection', 'quinine', 'chloroquine', 'mefloquine',
    'doxycycline', 'primaquine', 'atovaquone', 'proguanil'
]

# Define diagnosis patterns
DIABETES_ICD_CODES = ['E08', 'E09', 'E10', 'E11', 'E13']
MALARIA_ICD_CODES = ['B50', 'B51', 'B52', 'B53', 'B54']


class ReinforcementXGBoostTrainer:
    """
    Enhanced XGBoost trainer that incorporates reinforcement learning data
    """
    
    def __init__(self, disease_type, base_model_path=None):
        """
        Initialize the reinforcement learning trainer
        
        Args:
            disease_type: 'diabetes' or 'malaria'
            base_model_path: Path to existing base model (optional)
        """
        self.disease_type = disease_type
        self.base_model_path = base_model_path
        self.model = None
        self.feature_names = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
    def load_base_model(self):
        """Load existing base model if available"""
        if self.base_model_path and os.path.exists(self.base_model_path):
            try:
                with open(self.base_model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"✅ Loaded base model from {self.base_model_path}")
                return True
            except Exception as e:
                print(f"❌ Error loading base model: {e}")
        return False
    
    def get_reinforcement_data(self, period_start=None, period_end=None, min_confidence=0.7):
        """
        Get reinforcement learning data from prediction history
        
        Args:
            period_start: Start date for data collection
            period_end: End date for data collection
            min_confidence: Minimum confidence score for predictions to include
        """
        try:
            # Set default period if not provided (last 30 days)
            if not period_start:
                period_start = datetime.now().date() - timedelta(days=30)
            if not period_end:
                period_end = datetime.now().date()
            
            # Get predictions that are ready for learning
            predictions = PredictionHistory.objects.filter(
                timestamp__date__gte=period_start,
                timestamp__date__lte=period_end,
                disease_type=self.disease_type,
                is_learning_ready=True,
                confidence_score__gte=min_confidence
            ).order_by('-timestamp')
            
            print(f"📊 Found {predictions.count()} reinforcement learning records for {self.disease_type}")
            
            if predictions.count() == 0:
                print("⚠️ No reinforcement learning data available")
                return pd.DataFrame()
            
            # Convert to DataFrame
            reinforcement_data = []
            for pred in predictions:
                # Extract features from prediction
                features = self._extract_features_from_prediction(pred)
                
                # Create target based on actual outcome
                target = 1 if pred.status == 'confirmed' else 0
                
                # Add reinforcement learning weight based on learning score
                weight = pred.model_learning_score or 0.5
                
                reinforcement_data.append({
                    **features,
                    'target': target,
                    'weight': weight,
                    'prediction_id': pred.prediction_id,
                    'actual_disease': pred.actual_disease,
                    'medicine_prescribed': pred.medicine_prescribed,
                    'cost_of_treatment': float(pred.cost_of_treatment) if pred.cost_of_treatment else 0.0,
                    'confidence_score': pred.confidence_score,
                    'learning_score': pred.model_learning_score
                })
            
            return pd.DataFrame(reinforcement_data)
            
        except Exception as e:
            print(f"❌ Error getting reinforcement data: {e}")
            return pd.DataFrame()
    
    def _extract_features_from_prediction(self, prediction):
        """Extract features from a prediction history record"""
        try:
            # Extract temporal features
            schedule_date = prediction.schedule_date
            temporal_features = self._extract_temporal_features(schedule_date)
            
            # Extract medication features
            medicine_features = self._extract_medication_features(prediction.medicine_prescribed)
            
            # Basic features
            features = {
                'age_numeric': prediction.age,
                'is_male': 1 if prediction.gender.lower() == 'male' else 0,
                'is_pregnant': 1 if prediction.pregnant_patient else 0,
                'is_insured': 1 if prediction.nhia_patient else 0,
                'locality_encoded': hash(prediction.locality) % 100,
                'has_cost': 1 if prediction.cost_of_treatment and prediction.cost_of_treatment > 0 else 0,
                'cost_category': self._categorize_cost(prediction.cost_of_treatment),
                **temporal_features,
                **medicine_features
            }
            
            return features
            
        except Exception as e:
            print(f"❌ Error extracting features from prediction: {e}")
            return {}
    
    def _extract_temporal_features(self, date):
        """Extract temporal features from date"""
        try:
            return {
                'month': date.month,
                'year': date.year,
                'day_of_week': date.weekday(),
                'season': (date.month % 12 + 3) // 3,
                'is_weekend': 1 if date.weekday() >= 5 else 0
            }
        except:
            return {
                'month': 1, 'year': 2022, 'day_of_week': 0,
                'season': 1, 'is_weekend': 0
            }
    
    def _extract_medication_features(self, medicine_prescribed):
        """Extract medication-related features"""
        if not medicine_prescribed:
            return {
                'medication_count': 0,
                'has_medication': 0,
                f'{self.disease_type}_medication_present': 0
            }
        
        # Count medications
        medication_count = len(re.findall(r'\[.*?\]', medicine_prescribed))
        
        # Check for disease-specific medications
        medications = DIABETES_MEDICATIONS if self.disease_type == 'diabetes' else MALARIA_MEDICATIONS
        disease_medication_present = 0
        for med in medications:
            if med.lower() in medicine_prescribed.lower():
                disease_medication_present = 1
                break
        
        return {
            'medication_count': medication_count,
            'has_medication': 1 if medication_count > 0 else 0,
            f'{self.disease_type}_medication_present': disease_medication_present
        }
    
    def _categorize_cost(self, cost):
        """Categorize treatment cost"""
        if not cost:
            return 0
        cost_float = float(cost)
        if cost_float <= 10:
            return 0
        elif cost_float <= 50:
            return 1
        elif cost_float <= 100:
            return 2
        else:
            return 3
    
    def combine_training_data(self, base_data_path, reinforcement_data):
        """
        Combine base training data with reinforcement learning data
        
        Args:
            base_data_path: Path to base training data CSV
            reinforcement_data: DataFrame with reinforcement learning data
        """
        try:
            # Load base data
            if os.path.exists(base_data_path):
                base_data = pd.read_csv(base_data_path)
                print(f"📊 Loaded base data: {len(base_data)} records")
            else:
                print("⚠️ Base data not found, using only reinforcement data")
                base_data = pd.DataFrame()
            
            # Combine data
            if not base_data.empty and not reinforcement_data.empty:
                # Ensure consistent columns
                common_columns = list(set(base_data.columns) & set(reinforcement_data.columns))
                
                # Filter to common columns and combine
                base_filtered = base_data[common_columns]
                reinforcement_filtered = reinforcement_data[common_columns]
                
                # Add weight column to base data (default weight = 1.0)
                base_filtered['weight'] = 1.0
                
                # Combine datasets
                combined_data = pd.concat([base_filtered, reinforcement_filtered], ignore_index=True)
                print(f"📊 Combined data: {len(combined_data)} records ({len(base_filtered)} base + {len(reinforcement_filtered)} reinforcement)")
                
            elif not reinforcement_data.empty:
                combined_data = reinforcement_data
                print(f"📊 Using only reinforcement data: {len(combined_data)} records")
                
            else:
                print("❌ No training data available")
                return pd.DataFrame()
            
            return combined_data
            
        except Exception as e:
            print(f"❌ Error combining training data: {e}")
            return pd.DataFrame()
    
    def prepare_features(self, data):
        """Prepare features for model training"""
        try:
            # Define feature columns (same as in data_preprocessing_v2.py)
            feature_columns = [
                # Demographics
                'age_numeric', 'is_male', 'is_pregnant', 'is_insured',
                
                # Temporal features
                'month', 'year', 'day_of_week', 'season', 'is_weekend',
                
                # Clinical features
                'medication_count', 'has_medication',
                
                # Locality
                'locality_encoded',
                
                # Disease-specific medication features
                f'{self.disease_type}_medication_present',
                
                # Cost features
                'has_cost', 'cost_category'
            ]
            
            # Ensure all required features exist
            for col in feature_columns:
                if col not in data.columns:
                    data[col] = 0
            
            # Create feature matrix and target
            X = data[feature_columns]
            y = data['target']
            weights = data.get('weight', np.ones(len(data)))
            
            self.feature_names = feature_columns
            
            return X, y, weights
            
        except Exception as e:
            print(f"❌ Error preparing features: {e}")
            return None, None, None
    
    def train_model(self, X, y, weights=None, test_size=0.2):
        """Train XGBoost model with reinforcement learning data"""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Split weights if provided
            if weights is not None:
                train_weights = weights[X_train.index]
                test_weights = weights[X_test.index]
            else:
                train_weights = None
                test_weights = None
            
            # Initialize XGBoost model
            model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                eval_metric='logloss',
                use_label_encoder=False
            )
            
            # Train model with sample weights if available
            if train_weights is not None:
                print("🎯 Training with reinforcement learning weights...")
                model.fit(X_train, y_train, sample_weight=train_weights)
            else:
                print("🎯 Training without sample weights...")
                model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_pred_proba)
            
            # Calculate weighted metrics if weights are available
            if test_weights is not None:
                weighted_accuracy = accuracy_score(y_test, y_pred, sample_weight=test_weights)
                print(f"📊 Weighted accuracy: {weighted_accuracy:.4f}")
            
            print(f"\n{self.disease_type.title()} Model Results:")
            print(f"Accuracy: {accuracy:.4f}")
            print(f"AUC: {auc:.4f}")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
            print(f"Cross-validation accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print(f"\nTop 5 important features for {self.disease_type}:")
            print(feature_importance.head())
            
            self.model = model
            
            return model, X_test, y_test, y_pred, y_pred_proba, feature_importance
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
            return None, None, None, None, None, None
    
    def generate_shap_plots(self, X_test, output_dir="src/artifacts/reinforcement_shap_plots"):
        """Generate SHAP plots for the trained model"""
        if self.model is None:
            print("❌ No model available for SHAP analysis")
            return False
        
        try:
            print(f"\n📊 Generating SHAP plots for {self.disease_type}...")
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize SHAP explainer
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_test)
            
            # Set style for better plots
            plt.style.use('default')
            
            # Summary Plot
            plt.figure(figsize=(12, 8))
            shap.summary_plot(shap_values, X_test, feature_names=self.feature_names, show=False)
            plt.title(f'Reinforcement Learning SHAP Summary - {self.disease_type.title()}', fontsize=16, fontweight='bold')
            plt.tight_layout()
            summary_path = os.path.join(output_dir, f'{self.disease_type}_reinforcement_shap_summary.png')
            plt.savefig(summary_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Bar Plot
            plt.figure(figsize=(12, 8))
            shap.summary_plot(shap_values, X_test, feature_names=self.feature_names, plot_type="bar", show=False)
            plt.title(f'Reinforcement Learning Feature Importance - {self.disease_type.title()}', fontsize=16, fontweight='bold')
            plt.tight_layout()
            bar_path = os.path.join(output_dir, f'{self.disease_type}_reinforcement_shap_bar.png')
            plt.savefig(bar_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ SHAP plots saved to {output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating SHAP plots: {e}")
            return False
    
    def save_model(self, output_path):
        """Save the trained model"""
        try:
            if self.model is None:
                print("❌ No model to save")
                return False
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save model
            with open(output_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            # Save metadata
            metadata = {
                'disease_type': self.disease_type,
                'feature_names': self.feature_names,
                'training_date': datetime.now().isoformat(),
                'model_type': 'reinforcement_xgboost'
            }
            
            metadata_path = output_path.replace('.pkl', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Model saved to {output_path}")
            print(f"✅ Metadata saved to {metadata_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            return False
    
    def run_reinforcement_training(self, base_data_path=None, period_days=30, min_confidence=0.7):
        """
        Run complete reinforcement learning training pipeline
        
        Args:
            base_data_path: Path to base training data (optional)
            period_days: Number of days to look back for reinforcement data
            min_confidence: Minimum confidence score for reinforcement data
        """
        print(f"🚀 Starting reinforcement learning training for {self.disease_type}")
        print("=" * 60)
        
        try:
            # Load base model if available
            self.load_base_model()
            
            # Get reinforcement learning data
            period_start = datetime.now().date() - timedelta(days=period_days)
            reinforcement_data = self.get_reinforcement_data(
                period_start=period_start,
                min_confidence=min_confidence
            )
            
            if reinforcement_data.empty:
                print("❌ No reinforcement learning data available")
                return False
            
            # Combine with base data if available
            combined_data = self.combine_training_data(base_data_path, reinforcement_data)
            
            if combined_data.empty:
                print("❌ No training data available")
                return False
            
            # Prepare features
            X, y, weights = self.prepare_features(combined_data)
            
            if X is None:
                print("❌ Error preparing features")
                return False
            
            # Train model
            model, X_test, y_test, y_pred, y_pred_proba, feature_importance = self.train_model(X, y, weights)
            
            if model is None:
                print("❌ Error training model")
                return False
            
            # Generate SHAP plots
            self.generate_shap_plots(X_test)
            
            # Save model
            output_path = f"src/artifacts/models/{self.disease_type}_reinforcement_xgboost_model.pkl"
            self.save_model(output_path)
            
            print("\n" + "=" * 60)
            print(f"✅ Reinforcement learning training completed for {self.disease_type}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ Error in reinforcement training pipeline: {e}")
            return False


def main():
    """Main function to run reinforcement learning training for both diseases"""
    print("🚀 Starting Reinforcement Learning XGBoost Training")
    print("=" * 60)
    
    # Train diabetes model
    print("\n🎯 Training Diabetes Model with Reinforcement Learning")
    diabetes_trainer = ReinforcementXGBoostTrainer(
        disease_type='diabetes',
        base_model_path="src/artifacts/models/diabetes_xgboost_model_v2.pkl"
    )
    
    diabetes_success = diabetes_trainer.run_reinforcement_training(
        base_data_path="src/artifacts/formatted/diabetes_balanced_formatted.csv"
    )
    
    # Train malaria model
    print("\n🎯 Training Malaria Model with Reinforcement Learning")
    malaria_trainer = ReinforcementXGBoostTrainer(
        disease_type='malaria',
        base_model_path="src/artifacts/models/malaria_xgboost_model_v2.pkl"
    )
    
    malaria_success = malaria_trainer.run_reinforcement_training(
        base_data_path="src/artifacts/formatted/malaria_balanced_formatted.csv"
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("REINFORCEMENT LEARNING TRAINING SUMMARY")
    print("=" * 60)
    
    if diabetes_success:
        print("✅ Diabetes reinforcement learning training completed")
    else:
        print("❌ Diabetes reinforcement learning training failed")
    
    if malaria_success:
        print("✅ Malaria reinforcement learning training completed")
    else:
        print("❌ Malaria reinforcement learning training failed")
    
    print(f"\n📁 Models saved to: src/artifacts/models/")
    print(f"📁 SHAP plots saved to: src/artifacts/reinforcement_shap_plots/")


if __name__ == "__main__":
    main() 