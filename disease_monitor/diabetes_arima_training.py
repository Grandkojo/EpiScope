#!/usr/bin/env python3
"""
ARIMA Time Series Forecasting for Diabetes Cases
Comparison model to LSTM for diabetes case prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
import gc

# ARIMA and time series
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose

# Data preprocessing
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Suppress warnings
warnings.filterwarnings('ignore')

class DiabetesARIMAForecaster:
    def __init__(self, prediction_days=14, scaler_type='robust'):
        """
        Initialize the ARIMA forecaster
        
        Args:
            prediction_days: Number of days to predict ahead (default: 14 days)
            scaler_type: Type of scaler to use ('robust' or 'minmax')
        """
        self.prediction_days = prediction_days
        
        # Use specified scaler
        if scaler_type == 'minmax':
            self.scaler = MinMaxScaler()
            print("Using MinMaxScaler")
        else:
            self.scaler = RobustScaler()
            print("Using RobustScaler")
            
        self.model = None
        self.best_params = None
        
    def load_and_prepare_data(self, file_path):
        """
        Load and prepare diabetes data for ARIMA forecasting
        """
        print("📊 Loading diabetes data...")
        
        try:
            # Load the data
            df = pd.read_csv(file_path)
            print(f"📈 Raw data shape: {df.shape}")
            
            # Convert Schedule Date to datetime
            df['Schedule Date'] = pd.to_datetime(df['Schedule Date'], format='%Y-%m-%d', errors='coerce')
            
            # Remove rows with invalid dates
            df = df.dropna(subset=['Schedule Date'])
            
            # Sort by date
            df = df.sort_values('Schedule Date').reset_index(drop=True)
            
            print(f"📅 Date range: {df['Schedule Date'].min()} to {df['Schedule Date'].max()}")
            print(f"📈 Total records: {len(df)}")
            
            # Create daily case counts
            daily_cases = df.groupby('Schedule Date').size().reset_index(name='daily_cases')
            daily_cases = daily_cases.set_index('Schedule Date')
            
            # Fill missing dates with 0 cases
            date_range = pd.date_range(start=daily_cases.index.min(), 
                                      end=daily_cases.index.max(), 
                                      freq='D')
            daily_cases = daily_cases.reindex(date_range, fill_value=0)
            
            print(f"📊 Daily cases range: {daily_cases['daily_cases'].min():.1f} to {daily_cases['daily_cases'].max():.1f}")
            print(f"📊 Total days: {len(daily_cases)}")
            print(f"📊 Days with cases: {(daily_cases['daily_cases'] > 0).sum()}")
            print(f"📊 Days with zero cases: {(daily_cases['daily_cases'] == 0).sum()}")
            
            # Clear memory
            del df
            gc.collect()
            
            return daily_cases
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise
    
    def check_stationarity(self, series):
        """
        Check if the time series is stationary
        """
        print("🔍 Checking stationarity...")
        
        # Perform Augmented Dickey-Fuller test
        result = adfuller(series)
        
        print(f"   ADF Statistic: {result[0]:.4f}")
        print(f"   p-value: {result[1]:.4f}")
        print(f"   Critical values:")
        for key, value in result[4].items():
            print(f"      {key}: {value:.4f}")
        
        if result[1] <= 0.05:
            print("   ✅ Series is stationary (p-value <= 0.05)")
            return True
        else:
            print("   ❌ Series is not stationary (p-value > 0.05)")
            return False
    
    def make_stationary(self, series):
        """
        Make the series stationary using differencing
        """
        print("🔄 Making series stationary...")
        
        # Try first difference
        diff1 = series.diff().dropna()
        if self.check_stationarity(diff1):
            print("   ✅ First difference makes series stationary")
            return diff1, 1
        
        # Try second difference
        diff2 = diff1.diff().dropna()
        if self.check_stationarity(diff2):
            print("   ✅ Second difference makes series stationary")
            return diff2, 2
        
        # Try seasonal difference (7 days)
        seasonal_diff = series.diff(7).dropna()
        if self.check_stationarity(seasonal_diff):
            print("   ✅ Seasonal difference (7 days) makes series stationary")
            return seasonal_diff, 7
        
        print("   ⚠️ Could not make series stationary with simple differencing")
        return series, 0
    
    def find_best_arima_params(self, series, max_p=3, max_d=2, max_q=3):
        """
        Find the best ARIMA parameters using grid search
        """
        print("🔍 Finding best ARIMA parameters...")
        
        best_aic = float('inf')
        best_params = None
        
        # Grid search for ARIMA parameters
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        fitted_model = model.fit()
                        
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_params = (p, d, q)
                            
                    except:
                        continue
        
        print(f"   Best ARIMA parameters: {best_params} (AIC: {best_aic:.2f})")
        return best_params
    
    def split_data(self, daily_cases, test_months=5):
        """
        Split data into train/test sets using time-based splitting
        """
        print("✂️ Splitting data using time-based approach...")
        
        # Calculate test set size (last 5 months)
        test_days = min(150, len(daily_cases) // 4)
        
        # Split the data
        train_data = daily_cases[:-test_days]
        test_data = daily_cases[-test_days:]
        
        print(f"📊 Train: {len(train_data)} days")
        print(f"📊 Test: {len(test_data)} days")
        print(f"📅 Train period: {train_data.index[0].strftime('%Y-%m-%d')} to {train_data.index[-1].strftime('%Y-%m-%d')}")
        print(f"📅 Test period: {test_data.index[0].strftime('%Y-%m-%d')} to {test_data.index[-1].strftime('%Y-%m-%d')}")
        
        return train_data, test_data
    
    def build_and_train_model(self, train_data):
        """
        Build and train the ARIMA model
        """
        print("🏗️ Building and training ARIMA model...")
        
        # Check stationarity and make stationary if needed
        is_stationary = self.check_stationarity(train_data['daily_cases'])
        
        if not is_stationary:
            stationary_data, diff_order = self.make_stationary(train_data['daily_cases'])
            # Reconstruct the stationary series with dates
            stationary_series = pd.Series(stationary_data.values, index=stationary_data.index)
        else:
            stationary_series = train_data['daily_cases']
            diff_order = 0
        
        # Find best ARIMA parameters
        best_params = self.find_best_arima_params(stationary_series)
        
        # Build the model with the best parameters
        if diff_order > 0:
            # If we differenced the data, we need to adjust the d parameter
            p, d, q = best_params
            d += diff_order
            best_params = (p, d, q)
        
        print(f"   Final ARIMA parameters: {best_params}")
        
        # Fit the model
        self.model = ARIMA(train_data['daily_cases'], order=best_params)
        fitted_model = self.model.fit()
        
        self.best_params = best_params
        
        print("✅ ARIMA model trained successfully!")
        print(f"   AIC: {fitted_model.aic:.2f}")
        print(f"   BIC: {fitted_model.bic:.2f}")
        
        return fitted_model
    
    def make_predictions(self, test_data):
        """
        Make predictions on the test set
        """
        print("🔮 Making predictions...")
        
        # Make predictions for the test period
        forecast = self.model.forecast(steps=len(test_data))
        
        # Get the actual values
        actual = test_data['daily_cases'].values
        
        # Ensure non-negative predictions
        forecast = np.maximum(forecast, 0)
        
        return actual, forecast
    
    def evaluate_model(self, actual, predicted):
        """
        Evaluate the model performance
        """
        print("📊 Evaluating model...")
        
        # Calculate metrics
        mse = mean_squared_error(actual, predicted)
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mse)
        r2 = r2_score(actual, predicted)
        
        # Calculate MAPE
        mape = np.mean(np.abs((actual - predicted) / (actual + 1e-8))) * 100
        
        # Calculate Zero case accuracy
        actual_zeros = (actual == 0)
        predicted_zeros = (predicted < 0.5)
        zero_accuracy = np.mean(actual_zeros == predicted_zeros)
        
        print(f"📊 Test Results:")
        print(f"   MSE: {mse:.2f}")
        print(f"   MAE: {mae:.2f}")
        print(f"   RMSE: {rmse:.2f}")
        print(f"   R² Score: {r2:.4f}")
        print(f"   MAPE: {mape:.2f}%")
        print(f"   Zero case prediction accuracy: {zero_accuracy:.2%}")
        
        # Additional analysis
        print(f"\n📈 Prediction Analysis:")
        print(f"   Actual range: {actual.min():.1f} - {actual.max():.1f}")
        print(f"   Predicted range: {predicted.min():.1f} - {predicted.max():.1f}")
        
        return mse, mae, rmse, r2, mape, zero_accuracy
    
    def plot_results(self, actual, predicted, test_data, save_dir="src/artifacts/arima_results"):
        """
        Plot ARIMA results
        """
        print("📈 Creating plots...")

        # Create output directory
        os.makedirs(save_dir, exist_ok=True)

        # Plot 1: Predictions vs Actual
        plt.figure(figsize=(15, 6))
        
        plt.plot(test_data.index, actual, label='Actual', alpha=0.7, linewidth=2)
        plt.plot(test_data.index, predicted, label='Predicted', alpha=0.7, linewidth=2)
        
        plt.title('Diabetes Cases: Actual vs Predicted (ARIMA - Test Set)')
        plt.xlabel('Date')
        plt.ylabel('Daily Cases')
        plt.legend()
        plt.grid(True)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(f"{save_dir}/diabetes_arima_predictions.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 2: Smoothed predictions (7-day rolling average)
        plt.figure(figsize=(15, 6))
        
        # Calculate rolling averages
        actual_rolling = pd.Series(actual, index=test_data.index).rolling(window=7, min_periods=1).mean()
        predicted_rolling = pd.Series(predicted, index=test_data.index).rolling(window=7, min_periods=1).mean()
        
        plt.plot(test_data.index, actual_rolling, label='Actual (Rolling 7d Avg)', alpha=0.7, linewidth=2)
        plt.plot(test_data.index, predicted_rolling, label='Predicted (Rolling 7d Avg)', alpha=0.7, linewidth=2)
        
        plt.title('Diabetes Cases: Actual vs Predicted (ARIMA - 7d Rolling Average)')
        plt.xlabel('Date')
        plt.ylabel('Daily Cases (Rolling 7d Average)')
        plt.legend()
        plt.grid(True)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(f"{save_dir}/diabetes_arima_predictions_smoothed.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 3: Scatter plot
        plt.figure(figsize=(10, 8))
        plt.scatter(actual, predicted, alpha=0.6)
        plt.plot([actual.min(), actual.max()], [actual.min(), actual.max()], 'r--', lw=2)
        plt.xlabel('Actual Daily Cases')
        plt.ylabel('Predicted Daily Cases')
        plt.title('Diabetes Cases: Predicted vs Actual (ARIMA)')
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(f"{save_dir}/diabetes_arima_scatter.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 4: Residuals
        plt.figure(figsize=(15, 6))
        
        residuals = actual - predicted
        
        plt.subplot(1, 2, 1)
        plt.plot(test_data.index, residuals)
        plt.title('Residuals Over Time')
        plt.xlabel('Date')
        plt.ylabel('Residuals')
        plt.grid(True)
        plt.xticks(rotation=45)
        
        plt.subplot(1, 2, 2)
        plt.hist(residuals, bins=30, alpha=0.7)
        plt.title('Residuals Distribution')
        plt.xlabel('Residuals')
        plt.ylabel('Frequency')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/diabetes_arima_residuals.png", dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Plots saved to {save_dir}/")
    
    def save_model(self, save_path="src/artifacts/models/diabetes_arima_model.pkl"):
        """
        Save the trained model
        """
        print(f"💾 Saving model to {save_path}...")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save the model
        import pickle
        with open(save_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save the parameters
        params_path = save_path.replace('.pkl', '_params.pkl')
        with open(params_path, 'wb') as f:
            pickle.dump(self.best_params, f)
        
        print(f"✅ Model and parameters saved successfully!")
    
    def run_full_pipeline(self, data_path="src/artifacts/cleaned_data/weija_diabetes_cleaned.csv"):
        """
        Run the complete ARIMA forecasting pipeline
        """
        print("🚀 Starting Diabetes ARIMA Forecasting Pipeline")
        print("=" * 60)
        
        # Step 1: Load and prepare data
        daily_cases = self.load_and_prepare_data(data_path)
        
        # Step 2: Split data
        train_data, test_data = self.split_data(daily_cases)
        
        # Step 3: Build and train model
        fitted_model = self.build_and_train_model(train_data)
        
        # Step 4: Make predictions
        actual, predicted = self.make_predictions(test_data)
        
        # Step 5: Evaluate model
        mse, mae, rmse, r2, mape, zero_accuracy = self.evaluate_model(actual, predicted)
        
        # Step 6: Plot results
        self.plot_results(actual, predicted, test_data)
        
        # Step 7: Save model
        self.save_model()
        
        print("\n" + "=" * 60)
        print("✅ Diabetes ARIMA Forecasting Pipeline Completed!")
        print("=" * 60)
        
        return {
            'model': self.model,
            'best_params': self.best_params,
            'metrics': {'mse': mse, 'mae': mae, 'rmse': rmse, 'r2': r2, 'mape': mape, 'zero_accuracy': zero_accuracy},
            'actual': actual,
            'predicted': predicted,
            'test_data': test_data
        }

def main():
    """
    Main function to run the diabetes ARIMA forecasting
    """
    # Initialize the forecaster
    forecaster = DiabetesARIMAForecaster(
        prediction_days=14,  # Predict next 14 days
        scaler_type='robust'  # Use RobustScaler
    )
    
    # Run the full pipeline
    results = forecaster.run_full_pipeline()
    
    print(f"\n🎯 Final Results:")
    print(f"   MSE: {results['metrics']['mse']:.2f}")
    print(f"   MAE: {results['metrics']['mae']:.2f}")
    print(f"   RMSE: {results['metrics']['rmse']:.2f}")
    print(f"   R² Score: {results['metrics']['r2']:.4f}")
    print(f"   MAPE: {results['metrics']['mape']:.2f}%")
    print(f"   Zero case accuracy: {results['metrics']['zero_accuracy']:.2%}")
    
    print(f"\n✅ Model saved as: diabetes_arima_model.pkl")
    print(f"✅ Training completed successfully!")

if __name__ == "__main__":
    main() 