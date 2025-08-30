#!/usr/bin/env python3
"""
Run LSTM Model with 14-day predictions
Updated version with improved accuracy
"""

from diabetes_lstm_training import DiabetesLSTMForecaster, setup_colab

def main():
    """
    Run the LSTM model with 14-day predictions
    """
    print("🚀 Running LSTM Model with 14-day predictions")
    print("=" * 60)
    
    # Setup Colab optimizations
    setup_colab()
    
    # Initialize the forecaster with 14-day prediction
    forecaster = DiabetesLSTMForecaster(
        sequence_length=60,  # Look back 60 days for 14-day prediction
        prediction_days=14   # Predict next 14 days
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
        
        print(f"\n✅ Model saved as: best_diabetes_lstm_model_14d.h5")
        print(f"✅ Training completed successfully!")
    else:
        print("❌ Training failed or no results available")

if __name__ == "__main__":
    main() 