# Reinforcement Learning System for XGBoost Models

This guide explains how to use the reinforcement learning system that integrates prediction history with XGBoost model training for continuous model improvement.

## Overview

The reinforcement learning system allows the XGBoost models to learn from actual prediction outcomes and treatment patterns, improving their accuracy over time. The system includes:

1. **Prediction History Tracking** - Stores predictions with outcomes and reinforcement data
2. **Reinforcement Learning Data Aggregation** - Processes historical data for training
3. **Enhanced XGBoost Training** - Incorporates reinforcement learning data into model training
4. **Model Performance Monitoring** - Tracks improvements over time

## System Architecture

### Models

#### PredictionHistory
Stores prediction records with reinforcement learning data:
- Patient demographics and symptoms
- Model predictions and confidence scores
- Actual outcomes (confirmed/corrected/discarded)
- Treatment data (medicine prescribed, cost)
- Learning scores for reinforcement learning

#### ReinforcementLearningData
Aggregates reinforcement learning data for model training:
- Period-based aggregation of prediction outcomes
- Model performance metrics
- Treatment pattern analysis
- Medicine frequency tracking

#### ModelTrainingSession
Tracks model training sessions:
- Training parameters and metadata
- Performance metrics
- Model artifacts and logs

### Services

#### PredictionHistoryService
- Creates and manages prediction records
- Updates prediction statuses with reinforcement data
- Calculates learning scores
- Retrieves predictions for analysis

#### ReinforcementLearningService
- Aggregates reinforcement learning data
- Creates training sessions
- Provides learning statistics
- Manages model training metadata

## Usage Guide

### 1. Creating Predictions

When a user makes a prediction, create a prediction history record:

```python
from disease_monitor.prediction_service import PredictionHistoryService

# Create a new prediction
prediction = PredictionHistoryService.create_prediction(
    user=request.user,
    age=45,
    gender='Male',
    locality='Weija',
    schedule_date=datetime.now().date(),
    pregnant_patient=False,
    nhia_patient=False,
    vertex_ai_enabled=True,
    disease_type='diabetes',
    symptoms_description='Patient reports frequent urination and fatigue',
    predicted_disease='Type 2 Diabetes',
    confidence_score=0.897,
    hospital_name='Weija General Hospital'
)
```

### 2. Updating Prediction Outcomes

When the actual outcome is known, update the prediction with reinforcement data:

```python
# Update prediction with actual outcome
updated_prediction = PredictionHistoryService.update_prediction_status(
    prediction_id=prediction.prediction_id,
    status='confirmed',  # or 'corrected', 'discarded'
    actual_disease='Type 2 Diabetes',
    medicine_prescribed='METFORMIN[ DIAMET | 500MG | Tablet | BID | For 120 Days ]',
    cost_of_treatment=Decimal('50.00'),
    doctor_notes='Patient responded well to treatment'
)
```

### 3. Running Reinforcement Learning Training

Use the Django management command to train models with reinforcement learning:

```bash
# Train both diabetes and malaria models
python manage.py run_reinforcement_training --disease-type both

# Train only diabetes model
python manage.py run_reinforcement_training --disease-type diabetes

# Train with custom parameters
python manage.py run_reinforcement_training \
    --disease-type malaria \
    --period-days 60 \
    --min-confidence 0.8
```

### 4. Monitoring Learning Statistics

Get reinforcement learning statistics for the dashboard:

```python
from disease_monitor.prediction_service import ReinforcementLearningService

# Get learning statistics
stats = ReinforcementLearningService.get_learning_statistics(
    disease_type='diabetes',
    days_back=30
)

print(f"Total predictions: {stats['total_predictions']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Learning ready: {stats['learning_ready_predictions']}")
```

### 5. Data Aggregation

Manually trigger data aggregation for specific periods:

```python
# Aggregate data for a specific period
aggregated_data = ReinforcementLearningService.aggregate_learning_data(
    period_start=datetime.now().date() - timedelta(days=30),
    period_end=datetime.now().date(),
    disease_type='diabetes'
)

# Save aggregated data
saved_data = ReinforcementLearningService.save_aggregated_data(aggregated_data)
```

## API Endpoints

### Prediction History

- `GET /api/predictions/` - Get user's predictions
- `GET /api/predictions/user_predictions/` - Get filtered predictions
- `POST /api/predictions/{id}/update_status/` - Update prediction status
- `POST /api/predictions/{id}/add_feedback/` - Add feedback to prediction

### Reinforcement Learning

- `GET /api/reinforcement-learning/statistics/` - Get learning statistics
- `POST /api/reinforcement-learning/aggregate_data/` - Trigger data aggregation

### Model Training

- `GET /api/training-sessions/` - Get training sessions
- `POST /api/training-sessions/create_session/` - Create training session
- `POST /api/training-sessions/{id}/update_status/` - Update session status

### Dashboard

- `GET /api/prediction-dashboard/` - Get dashboard data
- `POST /api/submit-reinforcement-data/` - Submit reinforcement data

## Reinforcement Learning Process

### 1. Data Collection
- Predictions are made and stored in `PredictionHistory`
- Actual outcomes are recorded when available
- Treatment data (medicine, cost) is captured

### 2. Learning Score Calculation
The system calculates a learning score based on:
- Prediction accuracy (confirmed = 1.0, corrected = 0.0)
- Confidence score (higher confidence = higher weight)
- Cost efficiency (lower cost = higher score)

### 3. Data Aggregation
- Reinforcement learning data is aggregated by time periods
- Treatment patterns are analyzed
- Model performance metrics are calculated

### 4. Model Training
- Base training data is combined with reinforcement learning data
- Sample weights are applied based on learning scores
- XGBoost models are retrained with enhanced data

### 5. Performance Monitoring
- Model performance is tracked over time
- SHAP plots are generated for interpretability
- Training sessions are logged for analysis

## Configuration

### Learning Score Weights
The learning score calculation uses these weights:
- Prediction accuracy: 60%
- Confidence score: 30%
- Cost efficiency: 10%

### Training Parameters
Default XGBoost parameters:
- `n_estimators`: 100
- `max_depth`: 6
- `learning_rate`: 0.1
- `eval_metric`: 'logloss'

### Data Requirements
- Minimum confidence score: 0.7 (configurable)
- Minimum data period: 30 days (configurable)
- Minimum learning-ready predictions: 5

## File Structure

```
disease_monitor/
├── models.py                          # Database models
├── prediction_service.py              # Service classes
├── reinforcement_xgboost_training.py  # XGBoost training with RL
├── views.py                          # API views
├── serializers.py                    # API serializers
├── urls.py                           # API endpoints
├── management/
│   └── commands/
│       └── run_reinforcement_training.py  # Management command
├── reinforcement_learning_demo.py    # Demo script
└── REINFORCEMENT_LEARNING_GUIDE.md   # This guide
```

## Demo and Testing

### Run the Demo
```bash
cd disease_monitor
python reinforcement_learning_demo.py
```

This will:
1. Create sample prediction data
2. Demonstrate reinforcement learning statistics
3. Show data aggregation examples
4. Prepare XGBoost training data

### Test the System
```bash
# Create sample data
python reinforcement_learning_demo.py

# Run reinforcement learning training
python manage.py run_reinforcement_training --disease-type both

# Check results
ls src/artifacts/models/*reinforcement*.pkl
ls src/artifacts/reinforcement_shap_plots/
```

## Best Practices

### 1. Data Quality
- Ensure accurate outcome recording
- Validate medicine and cost data
- Regular data quality checks

### 2. Training Frequency
- Train models weekly or monthly
- Monitor performance improvements
- Adjust training parameters based on results

### 3. Model Validation
- Use cross-validation for reliable metrics
- Compare with baseline models
- Monitor for overfitting

### 4. Performance Monitoring
- Track success rates over time
- Monitor learning score distributions
- Analyze treatment pattern changes

## Troubleshooting

### Common Issues

1. **No reinforcement learning data available**
   - Check if predictions have been updated with outcomes
   - Verify minimum confidence score requirements
   - Ensure medicine and cost data is provided

2. **Training fails**
   - Check if base model files exist
   - Verify data file paths
   - Ensure sufficient training data

3. **Poor model performance**
   - Review learning score calculations
   - Check data quality and completeness
   - Adjust training parameters

### Debug Commands

```bash
# Check prediction history
python manage.py shell
>>> from disease_monitor.models import PredictionHistory
>>> PredictionHistory.objects.filter(is_learning_ready=True).count()

# Check learning statistics
>>> from disease_monitor.prediction_service import ReinforcementLearningService
>>> stats = ReinforcementLearningService.get_learning_statistics()
>>> print(stats)
```

## Future Enhancements

1. **Advanced Reinforcement Learning**
   - Multi-armed bandit algorithms
   - Contextual bandits for treatment optimization
   - Deep reinforcement learning integration

2. **Real-time Learning**
   - Online learning capabilities
   - Incremental model updates
   - Streaming data processing

3. **Advanced Analytics**
   - Treatment effectiveness analysis
   - Cost-benefit optimization
   - Patient outcome prediction

4. **Integration Features**
   - Electronic health record integration
   - Real-time prediction updates
   - Automated outcome tracking

## Support

For questions or issues with the reinforcement learning system:

1. Check the demo script for examples
2. Review the API documentation
3. Examine the model training logs
4. Contact the development team

The reinforcement learning system is designed to continuously improve XGBoost model performance by learning from real-world prediction outcomes and treatment patterns. 