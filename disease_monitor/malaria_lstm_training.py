#!/usr/bin/env python3
"""
LSTM Time Series Forecasting for Malaria Cases
Following the 8-step procedure from the tutorial:
1. Create a container (model)
2. First Brain (LSTM Layer 1)
3. Second Brain (LSTM Layer 2) 
4. Decision Making (Dense Layer)
5. Half Helpers Resting (Dropout)
6. Final Answer (Dense Layer)
7. Toy Review (Model Summary)
8. Learning Instructions (Compile)

Optimized for malaria patterns:
- Shorter transmission cycles (14-day lookback vs 30-day for diabetes)
- Seasonal outbreak patterns
- Weather dependency features
- Rapid transmission characteristics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os

# TensorFlow and Keras
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Data preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class MalariaLSTMForecaster:
    def __init__(self, sequence_length=14, prediction_days=7):
        """
        Initialize the LSTM forecaster for malaria
        
        Args:
            sequence_length: Number of days to look back (default: 14 days for malaria)
            prediction_days: Number of days to predict ahead (default: 7 days)
        """
        self.sequence_length = sequence_length
        self.prediction_days = prediction_days
        self.scaler = MinMaxScaler()
        self.model = None
        
    def load_and_prepare_data(self, file_path):
        """
        Load and prepare malaria data for LSTM forecasting
        """
        print("📊 Loading malaria data...")
        
        # Load the data
        df = pd.read_csv(file_path)
        
        # Convert Schedule Date to datetime
        df['Schedule Date'] = pd.to_datetime(df['Schedule Date'], format='%Y-%m-%d')
        
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
        
        print(f"📊 Daily cases range: {daily_cases['daily_cases'].min()} to {daily_cases['daily_cases'].max()}")
        
        return daily_cases
    
    def create_malaria_features(self, daily_cases):
        """
        Create malaria-specific features for better forecasting
        """
        print("🔧 Creating malaria-specific features...")
        
        # Basic features
        features = daily_cases.copy()
        
        # Temporal features (malaria-specific)
        features['day_of_week'] = features.index.dayofweek
        features['month'] = features.index.month
        features['year'] = features.index.year
        features['day_of_year'] = features.index.dayofyear
        features['week_of_year'] = features.index.isocalendar().week
        
        # Malaria-specific seasonal features
        features['is_rainy_season'] = ((features['month'] >= 4) & (features['month'] <= 10)).astype(int)
        features['is_peak_malaria'] = ((features['month'] >= 6) & (features['month'] <= 9)).astype(int)
        features['is_dry_season'] = ((features['month'] <= 3) | (features['month'] >= 11)).astype(int)
        
        # Shorter rolling windows for malaria (faster transmission)
        features['cases_3d_avg'] = features['daily_cases'].rolling(window=3).mean()
        features['cases_7d_avg'] = features['daily_cases'].rolling(window=7).mean()
        features['cases_14d_avg'] = features['daily_cases'].rolling(window=14).mean()
        features['cases_3d_std'] = features['daily_cases'].rolling(window=3).std()
        features['cases_7d_std'] = features['daily_cases'].rolling(window=7).std()
        features['cases_14d_std'] = features['daily_cases'].rolling(window=14).std()
        
        # Shorter lag features for malaria (faster transmission cycles)
        features['cases_lag_1'] = features['daily_cases'].shift(1)
        features['cases_lag_3'] = features['daily_cases'].shift(3)
        features['cases_lag_7'] = features['daily_cases'].shift(7)
        features['cases_lag_14'] = features['daily_cases'].shift(14)
        
        # Trend features (malaria-specific)
        features['cases_trend_3d'] = features['daily_cases'] - features['cases_lag_3']
        features['cases_trend_7d'] = features['daily_cases'] - features['cases_lag_7']
        features['cases_trend_14d'] = features['daily_cases'] - features['cases_lag_14']
        
        # Outbreak detection features
        features['cases_above_7d_avg'] = (features['daily_cases'] > features['cases_7d_avg']).astype(int)
        features['cases_above_14d_avg'] = (features['daily_cases'] > features['cases_14d_avg']).astype(int)
        
        # Rate of change features
        features['cases_rate_3d'] = features['daily_cases'] / (features['cases_lag_3'] + 1)
        features['cases_rate_7d'] = features['daily_cases'] / (features['cases_lag_7'] + 1)
        
        # Seasonal features
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        features['is_month_start'] = features.index.is_month_start.astype(int)
        features['is_month_end'] = features.index.is_month_end.astype(int)
        
        # Remove NaN values from rolling calculations
        features = features.dropna()
        
        print(f"✅ Created {len(features.columns)} malaria-specific features")
        return features
    
    def prepare_sequences(self, features, target_col='daily_cases'):
        """
        Prepare sequences for LSTM training
        """
        print("🔄 Preparing sequences...")
        
        # Scale the features
        scaled_data = self.scaler.fit_transform(features)
        
        X, y = [], []
        
        for i in range(self.sequence_length, len(scaled_data) - self.prediction_days + 1):
            # Input sequence
            X.append(scaled_data[i-self.sequence_length:i])
            # Target (next prediction_days values)
            y.append(scaled_data[i:i+self.prediction_days, features.columns.get_loc(target_col)])
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"📊 Sequences created: X shape {X.shape}, y shape {y.shape}")
        return X, y
    
    def split_data(self, X, y, test_months=5):
        """
        Split data into train/validation/test sets
        Use last 5 months of 2024 for testing
        """
        print("✂️ Splitting data...")
        
        # Calculate split points
        total_samples = len(X)
        
        # Use last 5 months of 2024 for testing (approximately 150 days)
        test_samples = min(150, total_samples // 4)
        val_samples = total_samples // 5
        
        train_end = total_samples - test_samples - val_samples
        
        # Split the data
        X_train = X[:train_end]
        y_train = y[:train_end]
        
        X_val = X[train_end:train_end + val_samples]
        y_val = y[train_end:train_end + val_samples]
        
        X_test = X[train_end + val_samples:]
        y_test = y[train_end + val_samples:]
        
        print(f"📊 Train: {X_train.shape[0]} samples")
        print(f"📊 Validation: {X_val.shape[0]} samples") 
        print(f"📊 Test: {X_test.shape[0]} samples")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def build_malaria_model(self, input_shape):
        """
        Build LSTM model optimized for malaria patterns
        """
        print("🏗️ Building malaria-optimized LSTM model...")
        
        # Step 1: Create a container (model)
        model = Sequential()
        
        # Step 2: First Brain (LSTM Layer 1) - Optimized for malaria patterns
        model.add(LSTM(units=64, return_sequences=True, input_shape=input_shape))
        
        # Step 3: Second Brain (LSTM Layer 2) - Add another brain for malaria decision making
        model.add(LSTM(units=32, return_sequences=False))
        
        # Step 4: Decision Making (Dense Layer) - Malaria-specific decision layer
        model.add(Dense(units=16))
        
        # Step 5: Half Helpers Resting (Dropout) - Prevent overfitting for malaria outbreaks
        model.add(Dropout(0.3))
        
        # Step 6: Final Answer (Dense Layer) - Malaria prediction output
        model.add(Dense(units=self.prediction_days))
        
        # Step 7: Toy Review (Model Summary) - Check how well the malaria model was built
        print("\n📋 Malaria Model Summary:")
        model.summary()
        
        # Step 8: Learning Instructions (Compile) - Teach the malaria model how to improve
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train_model(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """
        Train the malaria LSTM model
        """
        print("🎯 Training malaria model...")
        
        # Callbacks for better training (malaria-specific)
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=20,  # More patience for malaria patterns
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=15,
                min_lr=0.0001,
                verbose=1
            )
        ]
        
        # Train the model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def evaluate_model(self, X_test, y_test, features):
        """
        Evaluate the malaria model performance
        """
        print("📊 Evaluating malaria model...")
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Inverse transform predictions
        y_test_original = self.scaler.inverse_transform(
            np.zeros((len(y_test), len(features.columns)))
        )
        y_test_original[:, features.columns.get_loc('daily_cases')] = y_test.flatten()
        y_test_original = y_test_original[:, features.columns.get_loc('daily_cases')]
        
        y_pred_original = self.scaler.inverse_transform(
            np.zeros((len(y_pred), len(features.columns)))
        )
        y_pred_original[:, features.columns.get_loc('daily_cases')] = y_pred.flatten()
        y_pred_original = y_pred_original[:, features.columns.get_loc('daily_cases')]
        
        # Calculate metrics
        mse = mean_squared_error(y_test_original, y_pred_original)
        mae = mean_absolute_error(y_test_original, y_pred_original)
        rmse = np.sqrt(mse)
        
        print(f"📊 Malaria Test Results:")
        print(f"   MSE: {mse:.2f}")
        print(f"   MAE: {mae:.2f}")
        print(f"   RMSE: {rmse:.2f}")
        
        return y_test_original, y_pred_original, mse, mae, rmse
    
    def plot_malaria_results(self, history, y_test, y_pred, save_dir="src/artifacts/lstm_results"):
        """
        Plot malaria-specific training history and predictions
        """
        print("📈 Creating malaria plots...")
        
        # Create output directory
        os.makedirs(save_dir, exist_ok=True)
        
        # Plot 1: Training History
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss', color='red')
        plt.plot(history.history['val_loss'], label='Validation Loss', color='darkred')
        plt.title('Malaria Model Loss During Training')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(history.history['mae'], label='Training MAE', color='red')
        plt.plot(history.history['val_mae'], label='Validation MAE', color='darkred')
        plt.title('Malaria Model MAE During Training')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/malaria_lstm_training_history.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: Predictions vs Actual
        plt.figure(figsize=(15, 6))
        
        # Plot actual vs predicted for first 100 test samples
        n_samples = min(100, len(y_test))
        plt.plot(y_test[:n_samples], label='Actual', alpha=0.7, color='red')
        plt.plot(y_pred[:n_samples], label='Predicted', alpha=0.7, color='darkred')
        plt.title('Malaria Cases: Actual vs Predicted (Test Set)')
        plt.xlabel('Time Steps')
        plt.ylabel('Daily Cases')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/malaria_lstm_predictions.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 3: Scatter plot
        plt.figure(figsize=(10, 8))
        plt.scatter(y_test, y_pred, alpha=0.6, color='red')
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual Daily Cases')
        plt.ylabel('Predicted Daily Cases')
        plt.title('Malaria Cases: Predicted vs Actual')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/malaria_lstm_scatter.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Malaria plots saved to {save_dir}/")
    
    def save_model(self, save_path="src/artifacts/models/malaria_lstm_model.h5"):
        """
        Save the trained malaria model
        """
        print(f"💾 Saving malaria model to {save_path}...")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save the model
        self.model.save(save_path)
        
        # Save the scaler
        scaler_path = save_path.replace('.h5', '_scaler.pkl')
        import pickle
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"✅ Malaria model and scaler saved successfully!")
    
    def run_full_pipeline(self, data_path="src/artifacts/cleaned_data/weija_malaria_cleaned.csv"):
        """
        Run the complete malaria LSTM forecasting pipeline
        """
        print("🚀 Starting Malaria LSTM Forecasting Pipeline")
        print("=" * 60)
        
        # Step 1: Load and prepare data
        daily_cases = self.load_and_prepare_data(data_path)
        
        # Step 2: Create malaria-specific features
        features = self.create_malaria_features(daily_cases)
        
        # Step 3: Prepare sequences
        X, y = self.prepare_sequences(features)
        
        # Step 4: Split data
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, y)
        
        # Step 5: Build malaria-optimized model
        self.model = self.build_malaria_model(input_shape=(X.shape[1], X.shape[2]))
        
        # Step 6: Train model
        history = self.train_model(X_train, y_train, X_val, y_val)
        
        # Step 7: Evaluate model
        y_test_orig, y_pred_orig, mse, mae, rmse = self.evaluate_model(X_test, y_test, features)
        
        # Step 8: Plot results
        self.plot_malaria_results(history, y_test_orig, y_pred_orig)
        
        # Step 9: Save model
        self.save_model()
        
        print("\n" + "=" * 60)
        print("✅ Malaria LSTM Forecasting Pipeline Completed!")
        print("=" * 60)
        
        return {
            'model': self.model,
            'scaler': self.scaler,
            'metrics': {'mse': mse, 'mae': mae, 'rmse': rmse},
            'history': history
        }

def main():
    """
    Main function to run the malaria LSTM forecasting
    """
    # Initialize the malaria forecaster
    forecaster = MalariaLSTMForecaster(
        sequence_length=14,  # Look back 14 days (shorter for malaria)
        prediction_days=7    # Predict next 7 days
    )
    
    # Run the full pipeline
    results = forecaster.run_full_pipeline()
    
    print(f"\n🎯 Malaria Final Results:")
    print(f"   MSE: {results['metrics']['mse']:.2f}")
    print(f"   MAE: {results['metrics']['mae']:.2f}")
    print(f"   RMSE: {results['metrics']['rmse']:.2f}")

if __name__ == "__main__":
    main() 