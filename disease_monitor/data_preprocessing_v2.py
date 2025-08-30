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

# SHAP for model interpretability
import shap

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

def extract_age_numeric(age_input):
    """Extract numeric age from various formats (numeric, 'XX Year(s)', etc.)"""
    if pd.isna(age_input) or age_input == '':
        return np.nan
    
    # If already numeric, return as is
    if isinstance(age_input, (int, float)):
        return int(age_input)
    
    # If string, try to extract numeric value
    age_str = str(age_input)
    
    # Try to find numbers in the string
    numbers = re.findall(r'\d+', age_str)
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
    
    # Medication features for both diseases (input features)
    df_engineered['diabetes_medication_present'] = df_engineered['Medicine Prescribed'].apply(
        lambda x: check_medication_presence(x, DIABETES_MEDICATIONS)
    )
    df_engineered['malaria_medication_present'] = df_engineered['Medicine Prescribed'].apply(
        lambda x: check_medication_presence(x, MALARIA_MEDICATIONS)
    )
    
    # General medication features (input features)
    df_engineered['medication_count'] = df_engineered['Medicine Prescribed'].apply(count_medications)
    df_engineered['has_medication'] = (df_engineered['medication_count'] > 0).astype(int)
    
    # Binary encoding for categorical variables (input features)
    df_engineered['is_pregnant'] = (df_engineered['Pregnant Patient'].astype(str).str.lower() == 'yes').astype(int)
    df_engineered['is_insured'] = (df_engineered['NHIA Patient'].astype(str).str.lower() == 'insured').astype(int)
    df_engineered['is_male'] = (df_engineered['Gender'].astype(str).str.lower() == 'male').astype(int)
    
    # Locality features (input features)
    df_engineered['locality_encoded'] = df_engineered['Locality'].astype(str).apply(lambda x: hash(x) % 100)
    
    # Cost features (optional input features)
    if 'Cost of Treatment (GHS )' in df_engineered.columns:
        df_engineered['Cost of Treatment (GHS )'] = pd.to_numeric(df_engineered['Cost of Treatment (GHS )'], errors='coerce')
        df_engineered['has_cost'] = (df_engineered['Cost of Treatment (GHS )'] > 0).astype(int)
        df_engineered['cost_category'] = pd.cut(
            df_engineered['Cost of Treatment (GHS )'], 
            bins=[0, 10, 50, 100, float('inf')], 
            labels=[0, 1, 2, 3]  # Numeric categories
        ).fillna(0).astype(int)
    else:
        # Set default values when cost data is not available
        df_engineered['has_cost'] = 0
        df_engineered['cost_category'] = 0
    
    # REMOVED: Diagnosis features (Principal Diagnosis, Additional Diagnosis, ICD codes)
    # These are what we're predicting, not input features!
    
    return df_engineered

def create_balanced_dataset(diabetes_df, malaria_df, target_disease):
    """Create a balanced dataset with positive and negative cases"""
    
    if target_disease == 'diabetes':
        # Positive cases: diabetes dataset
        positive_cases = diabetes_df.copy()
        positive_cases['target'] = 1
        
        # Negative cases: malaria dataset (as they don't have diabetes)
        negative_cases = malaria_df.copy()
        negative_cases['target'] = 0
        
        print(f"Diabetes positive cases: {len(positive_cases)}")
        print(f"Diabetes negative cases (from malaria data): {len(negative_cases)}")
        
    else:  # malaria
        # Positive cases: malaria dataset
        positive_cases = malaria_df.copy()
        positive_cases['target'] = 1
        
        # Negative cases: diabetes dataset (as they don't have malaria)
        negative_cases = diabetes_df.copy()
        negative_cases['target'] = 0
        
        print(f"Malaria positive cases: {len(positive_cases)}")
        print(f"Malaria negative cases (from diabetes data): {len(negative_cases)}")
    
    # Combine positive and negative cases
    combined_df = pd.concat([positive_cases, negative_cases], ignore_index=True)
    
    # Shuffle the data
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Combined dataset shape: {combined_df.shape}")
    print(f"Target distribution: {combined_df['target'].value_counts()}")
    
    return combined_df

def prepare_features_for_model(df, disease_type):
    """Prepare features for model training"""
    
    # First engineer all features
    df_engineered = engineer_features(df, disease_type)
    
    # Create target variable based on diagnosis information (what we're predicting)
    if 'Principal Diagnosis' in df_engineered.columns:
        # Check if the diagnosis contains the disease name or ICD codes
        disease_keywords = {
            'diabetes': ['diabetes', 'E08', 'E09', 'E10', 'E11', 'E13'],
            'malaria': ['malaria', 'B50', 'B51', 'B52', 'B53', 'B54']
        }
        
        if disease_type.lower() in disease_keywords:
            keywords = disease_keywords[disease_type.lower()]
            df_engineered['target'] = df_engineered['Principal Diagnosis'].str.contains('|'.join(keywords), case=False, na=False).astype(int)
        else:
            # Default to 1 if disease_type matches
            df_engineered['target'] = (df_engineered['disease_type'] == disease_type).astype(int)
    else:
        # Fallback: if no diagnosis column, use disease_type column if available
        if 'disease_type' in df_engineered.columns:
            df_engineered['target'] = (df_engineered['disease_type'] == disease_type).astype(int)
        else:
            # Default fallback
            df_engineered['target'] = 1
    
    # Select features for the model (input features only)
    feature_columns = [
        # Demographics
        'age_numeric', 'is_male', 'is_pregnant', 'is_insured',
        
        # Temporal features
        'month', 'year', 'day_of_week', 'season', 'is_weekend',
        
        # Clinical features (medication-based)
        'medication_count', 'has_medication',
        
        # Locality (important for disease spread patterns)
        'locality_encoded',
        
        # Disease-specific medication features
        f'{disease_type}_medication_present'
    ]
    
    # Add cost features (will be set to 0 if not available)
    feature_columns.extend(['has_cost', 'cost_category'])
    
    # Ensure all required features exist
    for col in feature_columns:
        if col not in df_engineered.columns:
            df_engineered[col] = 0
    
    # Create feature matrix and target
    X = df_engineered[feature_columns]
    y = df_engineered['target']
    
    return X, y, feature_columns

def generate_shap_plots(model, X_test, feature_names, disease_type, output_dir="src/artifacts/shap_plots"):
    """
    Generate comprehensive SHAP plots for model interpretability
    
    Args:
        model: Trained XGBoost model
        X_test: Test data features
        feature_names: List of feature names
        disease_type: Name of the disease (diabetes/malaria)
        output_dir: Directory to save SHAP plots
    """
    print(f"\n📊 Generating SHAP plots for {disease_type}...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Initialize SHAP explainer
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        
        # Set style for better plots
        plt.style.use('default')
        
        # 1. Summary Plot (Beeswarm)
        plt.figure(figsize=(12, 8))
        shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
        plt.title(f'SHAP Summary Plot - {disease_type.title()}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        summary_path = os.path.join(output_dir, f'{disease_type}_shap_summary.png')
        plt.savefig(summary_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Summary plot saved: {summary_path}")
        
        # 2. Bar Plot (Feature Importance) - Fixed for better label visibility
        plt.figure(figsize=(12, 8))  # Increased figure size
        shap.summary_plot(shap_values, X_test, feature_names=feature_names, plot_type="bar", show=False)
        plt.title(f'SHAP Feature Importance - Malaria & Diabetes', fontsize=16, fontweight='bold')
        plt.xlabel('mean(|SHAP value|) (average impact on model output magnitude)', fontsize=12)
        plt.tight_layout(pad=2.0)  # Increased padding
        bar_path = os.path.join(output_dir, f'{disease_type}_shap_bar.png')
        plt.savefig(bar_path, dpi=300, bbox_inches='tight', pad_inches=0.3)  # Added padding
        plt.close()
        print(f"✅ Bar plot saved: {bar_path}")
        
        # 3. Waterfall Plot (for a sample case)
        plt.figure(figsize=(12, 8))
        shap.waterfall_plot(explainer.expected_value, shap_values[0], X_test.iloc[0], 
                           feature_names=feature_names, show=False)
        plt.title(f'SHAP Waterfall Plot - {disease_type.title()} (Sample Case)', fontsize=16, fontweight='bold')
        plt.tight_layout()
        waterfall_path = os.path.join(output_dir, f'{disease_type}_shap_waterfall.png')
        plt.savefig(waterfall_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Waterfall plot saved: {waterfall_path}")
        
        # 4. Force Plot (for a sample case)
        plt.figure(figsize=(12, 6))
        shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0], 
                       feature_names=feature_names, show=False, matplotlib=True)
        plt.title(f'SHAP Force Plot - {disease_type.title()} (Sample Case)', fontsize=16, fontweight='bold')
        plt.tight_layout()
        force_path = os.path.join(output_dir, f'{disease_type}_shap_force.png')
        plt.savefig(force_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Force plot saved: {force_path}")
        
        # 5. Dependence Plot (for top feature)
        top_feature_idx = np.argmax(np.abs(shap_values).mean(0))
        top_feature = feature_names[top_feature_idx]
        
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(top_feature_idx, shap_values, X_test, 
                           feature_names=feature_names, show=False)
        plt.title(f'SHAP Dependence Plot - {top_feature} ({disease_type.title()})', 
                 fontsize=16, fontweight='bold')
        plt.tight_layout()
        dependence_path = os.path.join(output_dir, f'{disease_type}_shap_dependence_{top_feature}.png')
        plt.savefig(dependence_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Dependence plot saved: {dependence_path}")
        
        # Save SHAP values for later use
        shap_values_path = os.path.join(output_dir, f'{disease_type}_shap_values.pkl')
        with open(shap_values_path, 'wb') as f:
            pickle.dump({
                'shap_values': shap_values,
                'expected_value': explainer.expected_value,
                'feature_names': feature_names
            }, f)
        print(f"✅ SHAP values saved: {shap_values_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating SHAP plots for {disease_type}: {e}")
        return False

def generate_shap_plots_generic(model, X_test, feature_names, disease_type, output_dir="src/artifacts/shap_plots"):
    """
    Generate SHAP plots with generic titles for the temporary script
    """
    print(f"\n📊 Generating SHAP plots for {disease_type}...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Initialize SHAP explainer
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        
        # Set style for better plots
        plt.style.use('default')
        
        # 1. Summary Plot (Beeswarm)
        plt.figure(figsize=(12, 8))
        shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
        plt.title(f'SHAP Summary Plot - {disease_type.title()}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        summary_path = os.path.join(output_dir, f'{disease_type}_shap_summary.png')
        plt.savefig(summary_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Summary plot saved: {summary_path}")
        
        # 2. Bar Plot (Feature Importance) - Fixed for better label visibility
        plt.figure(figsize=(12, 8))  # Increased figure size
        shap.summary_plot(shap_values, X_test, feature_names=feature_names, plot_type="bar", show=False)
        plt.title(f'SHAP Feature Importance - {disease_type.title()}', fontsize=16, fontweight='bold')
        plt.xlabel('mean(|SHAP value|) (average impact on model output magnitude)', fontsize=12)
        plt.tight_layout(pad=2.0)  # Increased padding
        bar_path = os.path.join(output_dir, f'{disease_type}_shap_bar.png')
        plt.savefig(bar_path, dpi=300, bbox_inches='tight', pad_inches=0.3)  # Added padding
        plt.close()
        print(f"✅ Bar plot saved: {bar_path}")
        
        # 3. Waterfall Plot (for a sample case)
        plt.figure(figsize=(12, 8))
        shap.waterfall_plot(explainer.expected_value, shap_values[0], X_test.iloc[0], 
                           feature_names=feature_names, show=False)
        plt.title(f'SHAP Waterfall Plot - {disease_type.title()} (Sample Case)', fontsize=16, fontweight='bold')
        plt.tight_layout()
        waterfall_path = os.path.join(output_dir, f'{disease_type}_shap_waterfall.png')
        plt.savefig(waterfall_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Waterfall plot saved: {waterfall_path}")
        
        # 4. Force Plot (for a sample case)
        plt.figure(figsize=(12, 6))
        shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0], 
                       feature_names=feature_names, show=False, matplotlib=True)
        plt.title(f'SHAP Force Plot - {disease_type.title()} (Sample Case)', fontsize=16, fontweight='bold')
        plt.tight_layout()
        force_path = os.path.join(output_dir, f'{disease_type}_shap_force.png')
        plt.savefig(force_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Force plot saved: {force_path}")
        
        # 5. Dependence Plot (for top feature)
        top_feature_idx = np.argmax(np.abs(shap_values).mean(0))
        top_feature = feature_names[top_feature_idx]
        
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(top_feature_idx, shap_values, X_test, 
                           feature_names=feature_names, show=False)
        plt.title(f'SHAP Dependence Plot - {top_feature} ({disease_type.title()})', 
                 fontsize=16, fontweight='bold')
        plt.tight_layout()
        dependence_path = os.path.join(output_dir, f'{disease_type}_shap_dependence_{top_feature}.png')
        plt.savefig(dependence_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Dependence plot saved: {dependence_path}")
        
        # Save SHAP values for later use
        shap_values_path = os.path.join(output_dir, f'{disease_type}_shap_values.pkl')
        with open(shap_values_path, 'wb') as f:
            pickle.dump({
                'shap_values': shap_values,
                'expected_value': explainer.expected_value,
                'feature_names': feature_names
            }, f)
        print(f"✅ SHAP values saved: {shap_values_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating SHAP plots for {disease_type}: {e}")
        return False

def train_xgboost_model(X, y, disease_type, test_size=0.2):
    """Train XGBoost model with cross-validation and SHAP analysis"""
    
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
    
    # Generate SHAP plots
    generate_shap_plots(model, X_test, X.columns.tolist(), disease_type)
    
    return model, X_test, y_test, y_pred, y_pred_proba, feature_importance

def main():
    """Main function to process data and train models"""
    
    # Define paths
    data_path = "src/artifacts/merged_data/"
    formatted_path = "src/artifacts/formatted/"
    models_path = "src/artifacts/models/"
    
    # Create directories if they don't exist
    os.makedirs(formatted_path, exist_ok=True)
    os.makedirs(models_path, exist_ok=True)
    
    print("🚀 Starting IMPROVED data preprocessing and model training...")
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
    
    # Create balanced datasets
    print("\nCreating balanced datasets...")
    diabetes_balanced = create_balanced_dataset(diabetes_engineered, malaria_engineered, 'diabetes')
    malaria_balanced = create_balanced_dataset(diabetes_engineered, malaria_engineered, 'malaria')
    
    # Prepare features for model training
    print("\nPreparing features for model training...")
    X_diabetes, y_diabetes, diabetes_features = prepare_features_for_model(diabetes_balanced, 'diabetes')
    X_malaria, y_malaria, malaria_features = prepare_features_for_model(malaria_balanced, 'malaria')
    
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
    diabetes_formatted = diabetes_balanced[['target'] + diabetes_features]
    diabetes_formatted.to_csv(os.path.join(formatted_path, 'diabetes_balanced_formatted.csv'), index=False)
    
    malaria_formatted = malaria_balanced[['target'] + malaria_features]
    malaria_formatted.to_csv(os.path.join(formatted_path, 'malaria_balanced_formatted.csv'), index=False)
    
    # Save models and metadata
    print("\nSaving models and metadata...")
    diabetes_model_path = os.path.join(models_path, 'diabetes_xgboost_model_v2.pkl')
    with open(diabetes_model_path, 'wb') as f:
        pickle.dump(diabetes_model, f)
    
    malaria_model_path = os.path.join(models_path, 'malaria_xgboost_model_v2.pkl')
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
    
    metadata_path = os.path.join(models_path, 'model_metadata_v2.json')
    with open(metadata_path, 'w') as f:
        json.dump(model_metadata, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("IMPROVED MODEL TRAINING SUMMARY")
    print("=" * 60)
    
    print(f"\n📊 Dataset Summary:")
    print(f"Diabetes balanced: {len(diabetes_balanced)} records")
    print(f"Malaria balanced: {len(malaria_balanced)} records")
    
    print(f"\n🔧 Features Used:")
    print(f"Diabetes: {len(diabetes_features)} features")
    print(f"Malaria: {len(malaria_features)} features")
    
    print(f"\n📁 Files Created:")
    print(f"Formatted data: {formatted_path}")
    print(f"Trained models: {models_path}")
    
    print(f"\n🎯 Model Performance:")
    print(f"Diabetes - Accuracy: {model_metadata['diabetes']['performance']['accuracy']:.4f}, AUC: {model_metadata['diabetes']['performance']['auc']:.4f}")
    print(f"Malaria - Accuracy: {model_metadata['malaria']['performance']['accuracy']:.4f}, AUC: {model_metadata['malaria']['performance']['auc']:.4f}")
    
    print(f"\n✅ IMPROVED training pipeline completed successfully!")

def generate_shap_for_existing_models():
    """
    Temporary function to generate SHAP plots for existing trained v2 models
    Run this function to create SHAP visualizations for your current models
    """
    print("🔍 Generating SHAP plots for existing v2 models...")
    print("=" * 60)
    
    # Define paths
    models_path = "src/artifacts/models/"
    data_path = "src/artifacts/merged_data/"
    
    # Load existing models
    try:
        # Load diabetes model
        with open(os.path.join(models_path, 'diabetes_xgboost_model_v2.pkl'), 'rb') as f:
            diabetes_model = pickle.load(f)
        print("✅ Loaded diabetes model")
        
        # Load malaria model
        with open(os.path.join(models_path, 'malaria_xgboost_model_v2.pkl'), 'rb') as f:
            malaria_model = pickle.load(f)
        print("✅ Loaded malaria model")
        
    except FileNotFoundError as e:
        print(f"❌ Error loading models: {e}")
        print("Make sure the v2 models exist in src/artifacts/models/")
        return
    
    # Load and prepare test data
    try:
        print("\n📊 Loading and preparing test data...")
        
        # Load datasets
        diabetes_df = pd.read_csv(os.path.join(data_path, "weija_diabetes_merged.csv"))
        malaria_df = pd.read_csv(os.path.join(data_path, "weija_malaria_merged.csv"))
        
        # Clean and engineer features
        diabetes_clean = clean_dataset(diabetes_df, 'diabetes')
        malaria_clean = clean_dataset(malaria_df, 'malaria')
        
        diabetes_engineered = engineer_features(diabetes_clean, 'diabetes')
        malaria_engineered = engineer_features(malaria_clean, 'malaria')
        
        # Create balanced datasets
        diabetes_balanced = create_balanced_dataset(diabetes_engineered, malaria_engineered, 'diabetes')
        malaria_balanced = create_balanced_dataset(diabetes_engineered, malaria_engineered, 'malaria')
        
        # Prepare features
        X_diabetes, y_diabetes, diabetes_features = prepare_features_for_model(diabetes_balanced, 'diabetes')
        X_malaria, y_malaria, malaria_features = prepare_features_for_model(malaria_balanced, 'malaria')
        
        print("✅ Test data prepared")
        
    except Exception as e:
        print(f"❌ Error preparing test data: {e}")
        return
    
    # Generate SHAP plots for diabetes
    print(f"\n📊 Generating SHAP plots for diabetes model...")
    diabetes_success = generate_shap_plots_generic(
        diabetes_model, 
        X_diabetes.sample(min(100, len(X_diabetes)), random_state=42),  # Sample for faster processing
        diabetes_features, 
        'diabetes',
        output_dir="src/artifacts/shap_plots"
    )
    
    # Generate SHAP plots for malaria
    print(f"\n📊 Generating SHAP plots for malaria model...")
    malaria_success = generate_shap_plots_generic(
        malaria_model, 
        X_malaria.sample(min(100, len(X_malaria)), random_state=42),  # Sample for faster processing
        malaria_features, 
        'malaria',
        output_dir="src/artifacts/shap_plots"
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("SHAP GENERATION SUMMARY")
    print("=" * 60)
    
    if diabetes_success:
        print("✅ Diabetes SHAP plots generated successfully")
    else:
        print("❌ Failed to generate diabetes SHAP plots")
    
    if malaria_success:
        print("✅ Malaria SHAP plots generated successfully")
    else:
        print("❌ Failed to generate malaria SHAP plots")
    
    print(f"\n📁 SHAP plots saved to: src/artifacts/shap_plots/")
    print("Files generated:")
    print("  - diabetes_shap_summary.png")
    print("  - diabetes_shap_bar.png")
    print("  - diabetes_shap_waterfall.png")
    print("  - diabetes_shap_force.png")
    print("  - diabetes_shap_dependence_[feature].png")
    print("  - malaria_shap_summary.png")
    print("  - malaria_shap_bar.png")
    print("  - malaria_shap_waterfall.png")
    print("  - malaria_shap_force.png")
    print("  - malaria_shap_dependence_[feature].png")
    print("  - diabetes_shap_values.pkl")
    print("  - malaria_shap_values.pkl")
    
    print("\n🎯 SHAP plots show:")
    print("  • Feature importance and impact")
    print("  • How each feature contributes to predictions")
    print("  • Individual case explanations")
    print("  • Feature interactions and dependencies")

if __name__ == "__main__":
    # Uncomment the line below to generate SHAP plots for existing models
    generate_shap_for_existing_models()
    
    # Run the main training pipeline (with SHAP included)
    main() 