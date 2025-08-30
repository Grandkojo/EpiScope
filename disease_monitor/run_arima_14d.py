#!/usr/bin/env python3
"""
Run ARIMA Model with 14-day predictions
Comparison model to LSTM
"""

from diabetes_arima_training import DiabetesARIMAForecaster

def main():
    """
    Run the ARIMA model with 14-day predictions
    """
    print("🚀 Running ARIMA Model with 14-day predictions")
    print("=" * 60)
    
    # Initialize the forecaster
    forecaster = DiabetesARIMAForecaster(
        prediction_days=14,  # Predict next 14 days
        scaler_type='robust'  # Use RobustScaler
    )
    
    # Run the full pipeline
    results = forecaster.run_full_pipeline()
    
    if results and results['metrics']:
        print(f"\n🎯 Final Results:")
        print(f"   MSE: {results['metrics']['mse']:.2f}")
        print(f"   MAE: {results['metrics']['mae']:.2f}")
        print(f"   RMSE: {results['metrics']['rmse']:.2f}")
        print(f"   R² Score: {results['metrics']['r2']:.4f}")
        print(f"   MAPE: {results['metrics']['mape']:.2f}%")
        print(f"   Zero case accuracy: {results['metrics']['zero_accuracy']:.2%}")
        
        print(f"\n✅ Model saved as: diabetes_arima_model.pkl")
        print(f"✅ Training completed successfully!")
    else:
        print("❌ Training failed or no results available")

if __name__ == "__main__":
    main() 