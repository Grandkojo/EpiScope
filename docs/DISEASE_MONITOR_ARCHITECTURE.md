# Disease Monitor Architecture

## Overview

The Disease Monitor system has been restructured to separate demographic/clinical feature analysis from symptom analysis, addressing the finding that symptoms have negligible impact on the main model's output as shown in SHAP analysis. The system now uses **Vertex AI** for advanced symptom analysis capabilities.

## Architecture Components

### 1. DiseaseMonitor Class
**Purpose**: Handles demographic and clinical feature analysis using traditional ML models.

**Key Features**:
- **Core Features**: `age`, `sex`, `pregnant_patient`, `nhia_patient`, `orgname`, `address_locality`, `disease_code`
- **Disease Code Extraction**: Automatically extracts ICD codes (e.g., E11.65) from diagnosis text
- **XGBoost Model**: Trained on demographic/clinical features only
- **SHAP Analysis**: Provides feature importance insights
- **Vertex AI Integration**: Uses Vertex AI for symptom analysis

**Key Methods**:
- `preprocess_data()`: Handles feature engineering and encoding
- `train_with_validation()`: Trains the demographic/clinical model
- `predict()`: Makes predictions with optional symptom integration
- `extract_disease_code()`: Extracts ICD codes from diagnosis text
- `analyze_symptoms_with_vertex_ai()`: Analyzes symptoms using Vertex AI

### 2. SymptomAnalyzer Class
**Purpose**: Handles symptom analysis using Vertex AI models.

**Key Features**:
- **Zero-shot Analysis**: Uses Vertex AI for immediate symptom assessment
- **Fine-tuning Support**: Can create and deploy custom Vertex AI models
- **Detailed Insights**: Provides comprehensive symptom analysis
- **Batch Processing**: Handles multiple symptom descriptions
- **Model Deployment**: Deploy custom models to endpoints for production use

**Key Methods**:
- `analyze_symptoms_zero_shot()`: Analyzes symptoms using Vertex AI
- `get_symptom_insights()`: Provides detailed medical insights
- `batch_analyze_symptoms()`: Processes multiple symptom descriptions
- `create_fine_tuning_dataset()`: Creates training data for fine-tuning
- `create_custom_model()`: Creates custom Vertex AI models
- `deploy_model()`: Deploys models to endpoints

## Data Flow

```
Patient Data
    ↓
┌─────────────────┐    ┌─────────────────┐
│ Demographic/    │    │ Symptom         │
│ Clinical        │    │ Analysis        │
│ Features        │    │ (Vertex AI)     │
│                 │    │                 │
│ - age           │    │ - symptom text  │
│ - sex           │    │ - disease name  │
│ - pregnancy     │    │ - risk score    │
│ - nhia_status   │    │ - confidence    │
│ - location      │    │ - insights      │
│ - disease_code  │    │                 │
└─────────────────┘    └─────────────────┘
    ↓                        ↓
┌─────────────────┐    ┌─────────────────┐
│ XGBoost Model   │    │ Symptom Score   │
│                 │    │                 │
│ - base_prob     │    │ - risk_score    │
│ - feature_imp   │    │ - key_matches   │
│ - SHAP values   │    │ - missing_symp  │
└─────────────────┘    └─────────────────┘
    ↓                        ↓
┌─────────────────────────────────────────┐
│ Combined Prediction                     │
│                                         │
│ combined_prob = 0.7 * base_prob +       │
│                 0.3 * symptom_score     │
└─────────────────────────────────────────┘
```

## Key Improvements

### 1. Feature Separation
- **Before**: Symptoms were included as features but showed negligible impact
- **After**: Symptoms analyzed separately using Vertex AI, demographic/clinical features handled by traditional ML

### 2. Disease Code Integration
- **New Feature**: Extracts ICD codes (e.g., E11.65) from diagnosis text
- **Benefit**: Provides structured disease information for better predictions

### 3. Advanced AI Integration
- **Vertex AI**: Uses Google's enterprise-grade AI platform
- **Fine-tuning**: Can create specialized models for specific diseases
- **Deployment**: Models can be deployed to production endpoints
- **Batch Processing**: Efficient handling of multiple cases

### 4. Combined Scoring
- **Weighted Average**: 70% demographic/clinical + 30% symptom analysis
- **Configurable**: Weights can be adjusted based on domain expertise
- **Transparent**: Both scores provided separately for interpretability

## Usage Examples

### Basic Usage
```python
from src.models.disease_monitor import DiseaseMonitor
from src.models.symptom_analyzer import SymptomAnalyzer

# Initialize with Vertex AI
project_id = "your-gcp-project-id"
location = "us-central1"

disease_monitor = DiseaseMonitor(
    project_id=project_id,
    location=location,
    model_name="gemini-1.5-pro"
)

symptom_analyzer = SymptomAnalyzer(
    project_id=project_id,
    location=location,
    model_name="gemini-1.5-pro"
)

# Patient data
patient_data = pd.DataFrame([{
    'age': 45, 'sex': 1, 'pregnant_patient': 0,
    'nhia_patient': 1, 'orgname': 'Hospital',
    'address_locality': 'Accra',
    'diagnosis': 'E11.65 [Type 2 diabetes mellitus]'
}])

# Symptoms
symptoms = "feeling thirsty, frequent urination, fatigue"

# Combined prediction
results = disease_monitor.predict(
    data=patient_data,
    disease_name='diabetes',
    symptoms_text=symptoms
)
```

### Symptom Analysis Only
```python
# Analyze symptoms separately
symptom_result = symptom_analyzer.analyze_symptoms_zero_shot(
    symptoms, 'diabetes'
)

# Get detailed insights
insights = symptom_analyzer.get_symptom_insights(
    symptoms, 'diabetes'
)
```

### Batch Processing
```python
# Process multiple symptom descriptions
symptoms_list = [
    "thirsty and tired",
    "headache and fever",
    "frequent urination"
]

batch_results = symptom_analyzer.batch_analyze_symptoms(
    symptoms_list, 'diabetes'
)
```

### Custom Model Creation
```python
# Create training data
training_data = symptom_analyzer.create_fine_tuning_dataset(
    'diabetes', positive_examples, negative_examples
)

# Create custom model
model_name = "diabetes-symptom-analyzer"
model_resource = symptom_analyzer.create_custom_model(model_name, training_data)

# Deploy to endpoint
endpoint_name = symptom_analyzer.deploy_model(model_name)
```

## Configuration

### Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### Google Cloud Setup
1. **Enable APIs**: Enable Vertex AI API in your Google Cloud project
2. **Service Account**: Create a service account with Vertex AI permissions
3. **Authentication**: Set up authentication using service account key or gcloud auth

### Model Weights
The combined prediction uses weighted averaging:
```python
combined_prob = 0.7 * base_probability + 0.3 * symptom_score
```

These weights can be adjusted based on:
- Data quality
- Domain expertise
- Validation results

## Benefits

1. **Better Performance**: Focuses on features that actually impact predictions
2. **Enterprise AI**: Uses Google's enterprise-grade Vertex AI platform
3. **Scalability**: Can handle large-scale deployments with custom models
4. **Flexibility**: Can use symptoms when available, fall back to demographic-only
5. **Production Ready**: Models can be deployed to production endpoints
6. **Transparency**: Both scores provided separately for clinical review

## Vertex AI Advantages

1. **Enterprise Features**: 
   - Model versioning and management
   - A/B testing capabilities
   - Monitoring and logging
   - Security and compliance

2. **Custom Models**:
   - Fine-tune models for specific diseases
   - Deploy to dedicated endpoints
   - Scale automatically

3. **Integration**:
   - Seamless Google Cloud integration
   - Built-in monitoring and alerting
   - Cost optimization features

## Future Enhancements

1. **Fine-tuned Models**: Create disease-specific Vertex AI models
2. **Dynamic Weights**: Adjust weights based on data availability
3. **Multi-disease Support**: Handle multiple diseases simultaneously
4. **Clinical Validation**: Integrate with clinical guidelines
5. **Real-time Updates**: Continuous model improvement with new data
6. **Model Monitoring**: Implement Vertex AI model monitoring
7. **A/B Testing**: Compare different model versions 