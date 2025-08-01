import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import re
import pickle
import os
import json
from pathlib import Path

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
from sklearn.feature_selection import SelectKBest, f_classif
import xgboost as xgb

warnings.filterwarnings('ignore')
np.random.seed(42)

# Define medication dictionaries
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

def clean_dataset(df, disease_type):
    """Clean and preprocess the dataset"""
    
    df_clean = df.copy()
    
    # Drop unnecessary columns
    columns_to_drop = [
        'Sr.No.', 'E-tracking Number', 'orgname', 'disease_type',
        'Type of Procedure(s) Requested', 'Type of Test(s) Requested', 'Test Result(s)',
        'Provisional Diagnosis', 'Outcome of Discharge', 'Surgical Procedure',
        'Date of Admission', 'Date of Discharge'
    ]
    
    # Drop columns that exist in the dataset
    existing_columns = [col for col in columns_to_drop if col in df_clean.columns]
    df_clean = df_clean.drop(columns=existing_columns)
    
    print(f"Dropped {len(existing_columns)} columns for {disease_type}")
    
    # Handle missing values
    df_clean['Medicine Prescribed'] = df_clean['Medicine Prescribed'].fillna('')
    df_clean['Medicine Dispensed'] = df_clean['Medicine Dispensed'].fillna('')
    df_clean['Principal Diagnosis'] = df_clean['Principal Diagnosis'].fillna('')
    df_clean['Additional Diagnosis'] = df_clean['Additional Diagnosis'].fillna('')
    df_clean['Locality'] = df_clean['Locality'].fillna('Unknown')
    df_clean['Occupation'] = df_clean['Occupation'].fillna('Unknown')
    df_clean['Ward/Room'] = df_clean['Ward/Room'].fillna('Unknown')
    
    # Handle cost column (optional parameter)
    if 'Cost of Treatment (GHS )' in df_clean.columns:
        df_clean['Cost of Treatment (GHS )'] = pd.to_numeric(df_clean['Cost of Treatment (GHS )'], errors='coerce')
        df_clean['Cost of Treatment (GHS )'] = df_clean['Cost of Treatment (GHS )'].fillna(0)
    
    return df_clean

def extract_age_numeric(age_str):
    """Extract numeric age from 'XX Year(s)' format"""
    if pd.isna(age_str) or age_str == '':
        return np.nan
    
    numbers = re.findall(r'\d+', str(age_str))
    if numbers:
        return int(numbers[0])
    return np.nan

def create_age_groups(age):
    """Create age groups"""
    if pd.isna(age):
        return 'Unknown'
    elif age < 18:
        return 'Child'
    elif age < 40:
        return 'Young Adult'
    elif age < 60:
        return 'Middle Aged'
    else:
        return 'Elderly'

def extract_temporal_features(date_str):
    """Extract temporal features from date"""
    try:
        date = pd.to_datetime(date_str)
        return {
            'month': date.month,
            'year': date.year,
            'day_of_week': date.dayofweek,
            'season': (date.month % 12 + 3) // 3,
            'is_weekend': 1 if date.dayofweek >= 5 else 0
        }
    except:
        return {
            'month': 1, 'year': 2022, 'day_of_week': 0,
            'season': 1, 'is_weekend': 0
        }

def check_medication_presence(medicine_str, medication_list):
    """Check if any disease-specific medication is present"""
    if pd.isna(medicine_str) or medicine_str == '':
        return 0
    
    medicine_lower = medicine_str.lower()
    for med in medication_list:
        if med.lower() in medicine_lower:
            return 1
    return 0

def check_icd_codes(diagnosis_str, icd_codes):
    """Check if any disease-specific ICD codes are present"""
    if pd.isna(diagnosis_str) or diagnosis_str == '':
        return 0
    
    for code in icd_codes:
        if code in diagnosis_str:
            return 1
    return 0

def count_medications(medicine_str):
    """Count number of medications prescribed"""
    if pd.isna(medicine_str) or medicine_str == '':
        return 0
    
    medicine_count = len(re.findall(r'\[.*?\]', medicine_str))
    return medicine_count

def engineer_features(df, disease_type):
    """Engineer features for the dataset"""
    
    df_engineered = df.copy()
    
    # Extract age features
    df_engineered['age_numeric'] = df_engineered['Age'].apply(extract_age_numeric)
    df_engineered['age_group'] = df_engineered['age_numeric'].apply(create_age_groups)
    
    # Extract temporal features
    temporal_features = df_engineered['Schedule Date'].apply(extract_temporal_features)
    df_engineered['month'] = temporal_features.apply(lambda x: x['month'])
    df_engineered['year'] = temporal_features.apply(lambda x: x['year'])
    df_engineered['day_of_week'] = temporal_features.apply(lambda x: x['day_of_week'])
    df_engineered['season'] = temporal_features.apply(lambda x: x['season'])
    df_engineered['is_weekend'] = temporal_features.apply(lambda x: x['is_weekend'])
    
    # Medication features
    if disease_type == 'diabetes':
        df_engineered['diabetes_medication_present'] = df_engineered['Medicine Prescribed'].apply(
            lambda x: check_medication_presence(x, DIABETES_MEDICATIONS)
        )
        df_engineered['diabetes_icd_present'] = df_engineered['Principal Diagnosis'].apply(
            lambda x: check_icd_codes(x, DIABETES_ICD_CODES)
        )
    else:  # malaria
        df_engineered['malaria_medication_present'] = df_engineered['Medicine Prescribed'].apply(
            lambda x: check_medication_presence(x, MALARIA_MEDICATIONS)
        )
        df_engineered['malaria_icd_present'] = df_engineered['Principal Diagnosis'].apply(
            lambda x: check_icd_codes(x, MALARIA_ICD_CODES)
        )
    
    # General medication features
    df_engineered['medication_count'] = df_engineered['Medicine Prescribed'].apply(count_medications)
    df_engineered['has_medication'] = (df_engineered['medication_count'] > 0).astype(int)
    
    # Diagnosis features
    df_engineered['diagnosis_count'] = df_engineered['Principal Diagnosis'].apply(
        lambda x: len(re.findall(r'\[.*?\]', str(x)))
    )
    
    # Binary encoding for categorical variables
    df_engineered['is_pregnant'] = (df_engineered['Pregnant Patient'] == 'Yes').astype(int)
    df_engineered['is_insured'] = (df_engineered['NHIA Patient'] == 'Insured').astype(int)
    df_engineered['is_male'] = (df_engineered['Gender'] == 'Male').astype(int)
    
    # Cost features (optional)
    if 'Cost of Treatment (GHS )' in df_engineered.columns:
        df_engineered['has_cost'] = (df_engineered['Cost of Treatment (GHS )'] > 0).astype(int)
        df_engineered['cost_category'] = pd.cut(
            df_engineered['Cost of Treatment (GHS )'], 
            bins=[0, 10, 50, 100, float('inf')], 
            labels=['Low', 'Medium', 'High', 'Very High']
        )
    
    return df_engineered

def create_target_variable(df, disease_type):
    """Create target variable based on medication and diagnosis"""
    
    df_target = df.copy()
    
    if disease_type == 'diabetes':
        # Positive if diabetes medication OR diabetes ICD code present
        df_target['target'] = (
            (df_target['diabetes_medication_present'] == 1) | 
            (df_target['diabetes_icd_present'] == 1)
        ).astype(int)
    else:  # malaria
        # Positive if malaria medication OR malaria ICD code present
        df_target['target'] = (
            (df_target['malaria_medication_present'] == 1) | 
            (df_target['malaria_icd_present'] == 1)
        ).astype(int)
    
    return df_target

def prepare_features_for_model(df, disease_type):
    """Prepare features for model training"""
    
    # Select features for model training
    feature_columns = [
        # Demographics
        'age_numeric', 'is_male', 'is_pregnant', 'is_insured',
        
        # Temporal features
        'month', 'year', 'day_of_week', 'season', 'is_weekend',
        
        # Clinical features
        'medication_count', 'has_medication', 'diagnosis_count',
        
        # Disease-specific features
        f'{disease_type}_medication_present', f'{disease_type}_icd_present'
    ]
    
    # Add cost features if available
    if 'Cost of Treatment (GHS )' in df.columns:
        feature_columns.extend(['has_cost'])
    
    # Create feature matrix
    X = df[feature_columns].copy()
    y = df['target']
    
    # Handle missing values in features
    X = X.fillna(X.median())
    
    return X, y, feature_columns

def train_xgboost_model(X, y, disease_type, test_size=0.2):
    """Train XGBoost model with cross-validation"""
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    # Initialize XGBoost model
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False
    )
    
    # Train model
    print(f"Training {disease_type} model...")
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"\n{disease_type.title()} Model Results:")
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
    
    print(f"\nTop 5 important features for {disease_type}:")
    print(feature_importance.head())
    
    return model, X_test, y_test, y_pred, y_pred_proba, feature_importance

def main():
    """Main function to process data and train models"""
    
    # Define paths - fixed for running from disease_monitor directory
    data_path = "src/artifacts/merged_data/"
    formatted_path = "src/artifacts/formatted/"
    models_path = "src/artifacts/models/"
    
    # Create directories if they don't exist
    os.makedirs(formatted_path, exist_ok=True)
    os.makedirs(models_path, exist_ok=True)
    
    print("🚀 Starting data preprocessing and model training...")
    print("=" * 60)
    
    # Load datasets
    print("Loading datasets...")
    diabetes_df = pd.read_csv(os.path.join(data_path, "weija_diabetes_merged.csv"))
    malaria_df = pd.read_csv(os.path.join(data_path, "weija_malaria_merged.csv"))
    
    print(f"Diabetes dataset shape: {diabetes_df.shape}")
    print(f"Malaria dataset shape: {malaria_df.shape}")
    
    # Clean datasets
    print("\nCleaning datasets...")
    diabetes_clean = clean_dataset(diabetes_df, 'diabetes')
    malaria_clean = clean_dataset(malaria_df, 'malaria')
    
    # Engineer features
    print("\nEngineering features...")
    diabetes_engineered = engineer_features(diabetes_clean, 'diabetes')
    malaria_engineered = engineer_features(malaria_clean, 'malaria')
    
    # Create target variables
    print("\nCreating target variables...")
    diabetes_target = create_target_variable(diabetes_engineered, 'diabetes')
    malaria_target = create_target_variable(malaria_engineered, 'malaria')
    
    print(f"Diabetes - Positive cases: {diabetes_target['target'].sum()} ({diabetes_target['target'].mean():.2%})")
    print(f"Malaria - Positive cases: {malaria_target['target'].sum()} ({malaria_target['target'].mean():.2%})")
    
    # Prepare features for model training
    print("\nPreparing features for model training...")
    X_diabetes, y_diabetes, diabetes_features = prepare_features_for_model(diabetes_target, 'diabetes')
    X_malaria, y_malaria, malaria_features = prepare_features_for_model(malaria_target, 'malaria')
    
    print(f"Diabetes features: {len(diabetes_features)}")
    print(f"Malaria features: {len(malaria_features)}")
    
    # Train models
    print("\nTraining models...")
    diabetes_model, X_test_diabetes, y_test_diabetes, y_pred_diabetes, y_pred_proba_diabetes, diabetes_importance = train_xgboost_model(
        X_diabetes, y_diabetes, 'diabetes'
    )
    
    malaria_model, X_test_malaria, y_test_malaria, y_pred_malaria, y_pred_proba_malaria, malaria_importance = train_xgboost_model(
        X_malaria, y_malaria, 'malaria'
    )
    
    # Save formatted datasets
    print("\nSaving formatted datasets...")
    diabetes_formatted = diabetes_target[['target'] + diabetes_features]
    diabetes_formatted.to_csv(os.path.join(formatted_path, 'diabetes_formatted.csv'), index=False)
    
    malaria_formatted = malaria_target[['target'] + malaria_features]
    malaria_formatted.to_csv(os.path.join(formatted_path, 'malaria_formatted.csv'), index=False)
    
    # Save models and metadata
    print("\nSaving models and metadata...")
    diabetes_model_path = os.path.join(models_path, 'diabetes_xgboost_model.pkl')
    with open(diabetes_model_path, 'wb') as f:
        pickle.dump(diabetes_model, f)
    
    malaria_model_path = os.path.join(models_path, 'malaria_xgboost_model.pkl')
    with open(malaria_model_path, 'wb') as f:
        pickle.dump(malaria_model, f)
    
    # Save feature information
    model_metadata = {
        'diabetes': {
            'features': diabetes_features,
            'feature_importance': diabetes_importance.to_dict('records'),
            'model_path': diabetes_model_path,
            'performance': {
                'accuracy': accuracy_score(y_test_diabetes, y_pred_diabetes),
                'auc': roc_auc_score(y_test_diabetes, y_pred_proba_diabetes)
            }
        },
        'malaria': {
            'features': malaria_features,
            'feature_importance': malaria_importance.to_dict('records'),
            'model_path': malaria_model_path,
            'performance': {
                'accuracy': accuracy_score(y_test_malaria, y_pred_malaria),
                'auc': roc_auc_score(y_test_malaria, y_pred_proba_malaria)
            }
        }
    }
    
    metadata_path = os.path.join(models_path, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(model_metadata, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("MODEL TRAINING SUMMARY")
    print("=" * 60)
    
    print(f"\n📊 Dataset Summary:")
    print(f"Diabetes: {diabetes_df.shape[0]} records, {diabetes_target['target'].sum()} positive cases ({diabetes_target['target'].mean():.2%})")
    print(f"Malaria: {malaria_df.shape[0]} records, {malaria_target['target'].sum()} positive cases ({malaria_target['target'].mean():.2%})")
    
    print(f"\n🔧 Features Used:")
    print(f"Diabetes: {len(diabetes_features)} features")
    print(f"Malaria: {len(malaria_features)} features")
    
    print(f"\n📁 Files Created:")
    print(f"Formatted data: {formatted_path}")
    print(f"Trained models: {models_path}")
    
    print(f"\n🎯 Model Performance:")
    print(f"Diabetes - Accuracy: {model_metadata['diabetes']['performance']['accuracy']:.4f}, AUC: {model_metadata['diabetes']['performance']['auc']:.4f}")
    print(f"Malaria - Accuracy: {model_metadata['malaria']['performance']['accuracy']:.4f}, AUC: {model_metadata['malaria']['performance']['auc']:.4f}")
    
    print(f"\n✅ Training pipeline completed successfully!")

if __name__ == "__main__":
    main() 