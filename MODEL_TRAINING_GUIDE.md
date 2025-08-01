# EpiScope Disease Prediction Model Training Guide

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Data Pipeline](#data-pipeline)
4. [Model Training Process](#model-training-process)
5. [Gemini Vertex AI Integration](#gemini-vertex-ai-integration)
6. [Model Storage & Loading](#model-storage--loading)
7. [Validation & Testing](#validation--testing)
8. [API Integration](#api-integration)
9. [SHAP Explanations](#shap-explanations)
10. [Best Practices](#best-practices)

## Overview

The EpiScope disease prediction system uses a hybrid approach combining:
- **XGBoost models** for demographic/clinical feature analysis
- **Gemini Vertex AI** for symptom analysis
- **Dynamic weighting** for final prediction
- **Conservative thresholds** (0.7) for medical safety

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Raw Data      │    │   XGBoost       │    │   Gemini        │
│   (Hospital     │───▶│   Model         │    │   Vertex AI     │
│   Health Data)  │    │   (Demographic) │    │   (Symptoms)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────────────────────────┐
                       │      Dynamic Weighting              │
                       │      & Threshold Logic              │
                       └─────────────────────────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Final         │
                       │   Prediction    │
                       └─────────────────┘
```

## Data Pipeline

### 1. Data Sources
- **HospitalHealthData**: Raw patient records from Django models
- **Disease**: Disease definitions and metadata
- **CommonSymptom**: Disease-specific symptom mappings

### 2. Data Preprocessing (`preprocess_data`)

```python
def preprocess_data(self, df, disease_type, training=True):
    # 1. Basic feature preprocessing
    df['age'] = df['age'].astype(float)
    df['sex'] = df['sex'].map({'Male': 1, 'Female': 0})
    df['pregnant_patient'] = df['pregnant_patient'].astype(int)
    df['nhia_patient'] = df['nhia_patient'].astype(int)
    
    # 2. Categorical feature handling
    df['orgname'] = df['orgname'].fillna('Unknown').astype(str)
    df['address_locality'] = df['address_locality'].fillna('Unknown').astype(str)
    
    # 3. Disease code extraction
    df['disease_code'] = df['principal_diagnosis_new'].apply(self.extract_disease_code)
    
    # 4. Label encoding (training vs inference)
    for col in ['orgname', 'address_locality', 'disease_code']:
        if training:
            self.label_encoders[col] = LabelEncoder()
            df[col] = self.label_encoders[col].fit_transform(df[col])
        else:
            # Handle unseen categories
            df[col] = self.label_encoders[col].transform(df[col])
    
    # 5. Feature scaling
    num_cols = ['age']
    if training:
        X[num_cols] = self.scaler.fit_transform(X[num_cols])
    else:
        X[num_cols] = self.scaler.transform(X[num_cols])
```

### 3. Feature Engineering
**Core Features:**
- `age`: Patient age (scaled)
- `sex`: Gender (1=Male, 0=Female)
- `pregnant_patient`: Pregnancy status
- `nhia_patient`: NHIA insurance status
- `orgname`: Hospital/organization (encoded)
- `address_locality`: Geographic location (encoded)
- `disease_code`: ICD-10 disease codes (encoded)

## Model Training Process

### 1. Command Execution
```bash
python manage.py train_disease_model --project-id YOUR_PROJECT_ID
```

### 2. Training Flow (`train_disease_model.py`)

```python
# 1. Load all hospital data
df = pd.DataFrame(list(HospitalHealthData.objects.all().values()))

# 2. For each disease in Disease table
for disease_obj in Disease.objects.all():
    disease_name = disease_obj.disease_name.lower()
    
    # 3. Filter positive cases
    pos_df = df[df['principal_diagnosis_new'].str.contains(disease_name, case=False)]
    
    # 4. Generate negative cases
    neg_df = monitor.generate_negative_cases(df, disease_name, n_negative=len(pos_df))
    
    # 5. Train model
    model, splits = monitor.train_with_validation(pos_df, neg_df, disease_type=disease_name, threshold=0.7)
    
    # 6. Save model and generate SHAP plots
    monitor.save_models(path=f'models/{disease_name}')
    monitor.generate_shap_explanations(combined_df, disease_name, path=model_dir)
```

### 3. Negative Case Generation

```python
def generate_negative_cases(self, df, disease_name, n_negative=None):
    # 1. Filter out cases containing disease name
    negative_mask = ~df['principal_diagnosis_new'].str.contains(disease_name, case=False)
    negative_cases = df[negative_mask].copy()
    
    # 2. Stratified sampling by age groups
    negative_cases['age_group'] = pd.cut(negative_cases['age'], bins=5)
    negative_sample = negative_cases.groupby('age_group').apply(
        lambda x: x.sample(min(len(x), n_negative // 5 + 1))
    ).head(n_negative)
    
    # 3. Add target labels
    negative_sample['target'] = 0
    return negative_sample
```

### 4. XGBoost Model Training

```python
def train_with_cross_validation(self, df_pos, df_neg, disease_type, threshold=0.7, cv_folds=5):
    # 1. Combine datasets
    df_pos['target'] = 1
    df_neg['target'] = 0
    combined_df = pd.concat([df_pos, df_neg], ignore_index=True)
    
    # 2. Preprocess data
    X, y, feature_cols = self.preprocess_data(combined_df, disease_type, training=True)
    
    # 3. Initialize XGBoost with optimized parameters
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    # 4. Cross-validation
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    scoring = {
        'precision': make_scorer(precision_score),
        'recall': make_scorer(recall_score),
        'f1': make_scorer(f1_score),
        'roc_auc': make_scorer(roc_auc_score, needs_proba=True)
    }
    
    # 5. Train final model
    model.fit(X, y)
    self.models[disease_type] = model
    self.threshold = threshold
```

## Gemini Vertex AI Integration

### 1. Initialization
```python
def _initialize_vertex_ai(self, project_id, location, model_name):
    vertexai.init(project=project_id, location=location)
    self.vertex_client = GenerativeModel(model_name)
```

### 2. Symptom Analysis
```python
def analyze_symptoms_with_vertex_ai(self, symptoms_text, disease_name):
    # 1. Get disease-specific symptoms from database
    disease_obj = Disease.objects.get(disease_name__iexact=disease_name)
    expected_symptoms = list(CommonSymptom.objects.filter(disease=disease_obj).values_list('symptom', flat=True))
    
    # 2. Create prompt
    prompt = f"""
    Analyze the following symptoms for {disease_name} risk assessment.
    
    Patient symptoms: {symptoms_text}
    Expected symptoms for {disease_name}: {', '.join(expected_symptoms)}
    
    Please provide a risk score between 0 and 1 where:
    - 0.0-0.2: Very low risk (symptoms completely unrelated)
    - 0.2-0.4: Low risk (vaguely related)
    - 0.4-0.6: Moderate risk (some match)
    - 0.6-0.8: High risk (strong match)
    - 0.8-1.0: Very high risk (classic symptoms)
    
    IMPORTANT: Be very strict about symptom relevance.
    Return only the numerical score (e.g., 0.15).
    """
    
    # 3. Get response and extract score
    response = self.vertex_client.generate_content(prompt)
    score_text = response.text.strip()
    score_match = re.search(r'0\.\d+|\d+\.\d+', score_text)
    return float(score_match.group()) if score_match else 0.5
```

## Model Storage & Loading

### 1. Model Storage
```python
def save_models(self, path='models'):
    os.makedirs(path, exist_ok=True)
    for disease_name, model in self.models.items():
        joblib.dump(model, f'{path}/{disease_name}_model.joblib')
    joblib.dump(self.label_encoders, f'{path}/label_encoders.joblib')
    joblib.dump(self.scaler, f'{path}/scaler.joblib')
```

### 2. Model Loading
```python
def load_models(self, path='models'):
    for fname in os.listdir(path):
        if fname.endswith('_model.joblib'):
            disease_name = fname.replace('_model.joblib', '')
            self.models[disease_name] = joblib.load(os.path.join(path, fname))
    self.label_encoders = joblib.load(f'{path}/label_encoders.joblib')
    self.scaler = joblib.load(f'{path}/scaler.joblib')
```

### 3. File Structure
```
models/
├── diabetes/
│   ├── diabetes_model.joblib
│   ├── label_encoders.joblib
│   ├── scaler.joblib
│   └── diabetes/
│       └── shap/
│           ├── shap_summary_diabetes.png
│           ├── shap_bar_diabetes.png
│           ├── shap_interaction_diabetes.png
│           └── shap_waterfall_diabetes.png
└── malaria/
    └── ...
```

## Validation & Testing

### 1. Cross-Validation Metrics
- **Precision**: Accuracy of positive predictions
- **Recall**: Sensitivity (true positive rate)
- **F1-Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Area under ROC curve

### 2. Model Performance Logging
```python
logger.info(f"{disease_type} CV precision: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
logger.info(f"{disease_type} CV recall: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
logger.info(f"{disease_type} CV f1: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
logger.info(f"{disease_type} CV roc_auc: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
```

## API Integration

### 1. Prediction Flow
```python
def predict(self, data, disease_name, symptoms_text=None):
    # 1. Get XGBoost prediction
    X, _, _ = self.preprocess_data(data, disease_name, training=False)
    model = self.models[disease_name]
    base_probabilities = model.predict_proba(X)[:, 1]
    
    # 2. Get Gemini symptom analysis
    if symptoms_text:
        symptom_score = self.analyze_symptoms_with_vertex_ai(symptoms_text, disease_name)
    
    # 3. Dynamic weighting
    base_pred = 1 if base_prob >= 0.7 else 0
    symptom_pred = 1 if symptom_score >= 0.5 else 0
    
    if base_pred != symptom_pred:
        # Contradiction: give more weight to symptoms
        symptom_weight = 0.7
        base_weight = 0.3
    else:
        # Agreement: balanced weights
        symptom_weight = 0.5
        base_weight = 0.5
    
    # 4. Combine scores
    combined_prob = base_weight * base_prob + symptom_weight * symptom_score
    
    # 5. Dynamic threshold
    if symptom_score < 0.3:
        dynamic_threshold = 0.8
    elif symptom_score < 0.5:
        dynamic_threshold = 0.75
    else:
        dynamic_threshold = 0.7
    
    return {
        "base_probability": base_prob,
        "symptom_score": symptom_score,
        "combined_probability": combined_prob,
        "prediction": int(combined_prob >= dynamic_threshold),
        "dynamic_threshold": dynamic_threshold
    }
```

### 2. API Response Format
```json
{
    "prediction": 0,
    "base_probability": 0.996,
    "symptom_score": 0.25,
    "combined_probability": 0.474,
    "dynamic_threshold": 0.8,
    "uncertainty_reason": "symptom_contradiction"
}
```

## SHAP Explanations

### 1. SHAP Plot Generation
```python
def generate_shap_explanations(self, df, disease_name, path='models'):
    # 1. Get SHAP values
    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)
    
    # 2. Generate different plot types
    # Summary plot (beeswarm)
    shap.plots.beeswarm(shap_values, show=False)
    plt.savefig(f'{shap_dir}/shap_summary_{disease_name}.png')
    
    # Bar plot (feature importance)
    shap.plots.bar(shap_values, show=False)
    plt.savefig(f'{shap_dir}/shap_bar_{disease_name}.png')
    
    # Interaction plot
    shap.plots.interaction(shap_values, show=False)
    plt.savefig(f'{shap_dir}/shap_interaction_{disease_name}.png')
    
    # Waterfall plot (individual case)
    shap.plots.waterfall(shap_values[0], show=False)
    plt.savefig(f'{shap_dir}/shap_waterfall_{disease_name}.png')
```

### 2. SHAP Plot Types
- **Summary Plot**: Shows all features and their impact
- **Bar Plot**: Feature importance ranking
- **Interaction Plot**: Feature interaction effects
- **Waterfall Plot**: Individual case breakdown

## Best Practices

### 1. Medical Safety
- **Conservative threshold (0.7)**: Reduces false positives
- **Dynamic weighting**: Gives more weight to symptoms when they contradict demographics
- **Uncertainty handling**: Returns "uncertain" for borderline cases

### 2. Model Performance
- **Cross-validation**: 5-fold stratified CV for robust evaluation
- **Balanced datasets**: Equal positive/negative cases
- **Feature scaling**: StandardScaler for numerical features
- **Label encoding**: Handles categorical features properly

### 3. Data Quality
- **Missing value handling**: Fill with "Unknown" for categorical, mean for numerical
- **Outlier detection**: XGBoost handles outliers well
- **Feature engineering**: Extract disease codes from diagnosis text

### 4. Monitoring
- **SHAP explanations**: Understand model decisions
- **Performance metrics**: Track precision, recall, F1, AUC
- **Logging**: Comprehensive logging for debugging

### 5. Deployment
- **Model versioning**: Save models with timestamps
- **Backup**: Keep multiple model versions
- **Testing**: Validate on unseen data before deployment

## Troubleshooting

### Common Issues
1. **SHAP plots showing only 2 features**: Use `shap.plots.beeswarm()` instead of `shap.summary_plot()`
2. **Pickling errors**: Ensure classes are defined at module level
3. **Vertex AI errors**: Check project ID and authentication
4. **Memory issues**: Reduce dataset size or use sampling

### Performance Optimization
1. **Feature selection**: Remove low-importance features
2. **Hyperparameter tuning**: Use GridSearchCV for XGBoost
3. **Data augmentation**: Generate more training samples
4. **Model ensemble**: Combine multiple models

This guide covers the complete lifecycle of the EpiScope disease prediction system from data ingestion to API deployment. 