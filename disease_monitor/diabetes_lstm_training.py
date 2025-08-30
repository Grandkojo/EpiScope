#!/usr/bin/env python3
"""
LSTM Time Series Forecasting for Diabetes Cases with Weekly Aggregation

IMPROVED VERSION WITH WEEKLY APPROACH:
- Weekly aggregation for more stable patterns
- Enhanced feature engineering for weekly data
- Improved model architecture
- Better evaluation metrics
- 2-week prediction capability
- Smooth transitions between low and high values
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
import gc

# TensorFlow and Keras
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, LeakyReLU
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

# Data preprocessing
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def setup_colab():
    """Setup optimizations for Google Colab"""
    print("🚀 Setting up optimizations...")
    
    # Check GPU availability
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✅ GPU detected: {len(gpus)} GPU(s) available")
        # Enable memory growth to avoid OOM errors
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    else:
        print("⚠️ No GPU detected, using CPU")
    
    # Set mixed precision for faster training
    tf.keras.mixed_precision.set_global_policy('mixed_float16')
    
    # Optimize for performance
    tf.config.optimizer.set_jit(True)
    print("✅ Optimizations completed!")

class DiabetesLSTMForecaster:
    def __init__(self, sequence_length=30, prediction_days=14, min_cases=1, add_noise=True):
        """
        Initialize the LSTM forecaster with daily approach and improved zero-handling
        
        Args:
            sequence_length: Number of days to look back
            prediction_days: Number of days to predict ahead
            min_cases: Minimum number of cases (replaces zeros)
            add_noise: Whether to add small random noise to min_cases
        """
        self.sequence_length = sequence_length
        self.prediction_days = prediction_days
        self.min_cases = min_cases
        self.add_noise = add_noise
        # Use MinMaxScaler for better handling of daily data
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        self.model = None
        self.feature_names = None
        
    def load_and_prepare_data(self, file_path):
        """
        Load and prepare diabetes data with improved daily aggregation and zero-handling
        """
        print("📊 Loading diabetes data with improved daily aggregation...")
        
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
            
            # Fill missing dates with min_cases instead of 0
            date_range = pd.date_range(start=daily_cases.index.min(), end=daily_cases.index.max(), freq='D')
            daily_cases = daily_cases.reindex(date_range, fill_value=self.min_cases)
            
            # Check data variation
            case_variation = daily_cases['daily_cases'].std()
            print(f"📊 Case variation (std): {case_variation:.4f}")
            
            # Improved zero-handling: Use adaptive noise based on data characteristics
            zero_days = (daily_cases['daily_cases'] == 0).sum()
            total_days = len(daily_cases)
            zero_percentage = (zero_days / total_days) * 100
            
            print(f"📊 Zero days: {zero_days} ({zero_percentage:.1f}%)")
            print(f"📊 Non-zero days: {total_days - zero_days}")
            
            # Adaptive noise strategy based on zero percentage
            if zero_percentage > 50:
                # High zero percentage: use conservative noise
                noise_factor = 0.1
                print(f"⚠️ High zero percentage detected. Using conservative noise (factor: {noise_factor})")
            elif zero_percentage > 20:
                # Medium zero percentage: use moderate noise
                noise_factor = 0.2
                print(f"⚠️ Medium zero percentage detected. Using moderate noise (factor: {noise_factor})")
            else:
                # Low zero percentage: use minimal noise
                noise_factor = 0.05
                print(f"✅ Low zero percentage. Using minimal noise (factor: {noise_factor})")
            
            # Apply adaptive noise to zero and near-zero values
            if self.add_noise:
                # Add noise only to zero and very low values
                low_value_mask = daily_cases['daily_cases'] <= self.min_cases
                noise = np.random.uniform(0, noise_factor, size=len(daily_cases))
                daily_cases.loc[low_value_mask, 'daily_cases'] = self.min_cases + noise[low_value_mask]
            
            print(f"📊 Daily cases range: {daily_cases['daily_cases'].min():.2f} to {daily_cases['daily_cases'].max():.2f}")
            print(f"📊 Total days: {len(daily_cases)}")
            print(f"📊 Days with minimum cases: {(daily_cases['daily_cases'] <= self.min_cases + 0.1).sum()}")
            print(f"📊 Average cases per day: {daily_cases['daily_cases'].mean():.2f}")
            print(f"📊 Final case variation (std): {daily_cases['daily_cases'].std():.4f}")
            
            # Clear memory
            del df
            gc.collect()
            
            return daily_cases
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise
    
    def create_features(self, daily_cases):
        """
        Create sophisticated features to capture volatility patterns
        """
        print("🔧 Creating sophisticated daily features...")

        # Basic features
        features = daily_cases.copy()
        
        # Log transform for better handling of small values
        features['log_cases'] = np.log1p(features['daily_cases'])

        # Temporal features
        features['day_of_week'] = features.index.dayofweek
        features['month'] = features.index.month
        features['year'] = features.index.year
        features['day_of_year'] = features.index.dayofyear
        features['week_of_year'] = features.index.isocalendar().week
        features['quarter'] = features.index.quarter

        # Enhanced lag features with log transform
        for lag in [1, 2, 3, 7, 14, 21, 28, 30]:
            features[f'log_cases_lag_{lag}'] = features['log_cases'].shift(lag).fillna(np.log1p(self.min_cases))
            features[f'cases_lag_{lag}'] = features['daily_cases'].shift(lag).fillna(self.min_cases)
        
        # Volatility features - key for capturing patterns
        for window in [7, 14, 21, 30]:
            # Rolling volatility (standard deviation)
            features[f'volatility_{window}d'] = features['daily_cases'].rolling(window=window, min_periods=1).std().fillna(0.01)
            features[f'log_volatility_{window}d'] = features['log_cases'].rolling(window=window, min_periods=1).std().fillna(0.01)
            
            # Rolling mean
            features[f'cases_{window}d_avg'] = features['daily_cases'].rolling(window=window, min_periods=1).mean()
            features[f'log_cases_{window}d_avg'] = features['log_cases'].rolling(window=window, min_periods=1).mean()
            
            # Coefficient of variation (volatility relative to mean)
            features[f'cv_{window}d'] = features[f'volatility_{window}d'] / (features[f'cases_{window}d_avg'] + 1e-8)
        
        # Momentum and trend features
        for window in [7, 14, 21]:
            # Price rate of change
            features[f'momentum_{window}d'] = (features['daily_cases'] - features[f'cases_lag_{window}']) / (features[f'cases_lag_{window}'] + 1e-8)
            
            # Log momentum
            features[f'log_momentum_{window}d'] = features['log_cases'] - features[f'log_cases_lag_{window}']
            
            # Trend strength (linear regression slope)
            features[f'trend_{window}d'] = features['daily_cases'].rolling(window=window, min_periods=1).apply(
                lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0, raw=True
            ).fillna(0)
        
        # Seasonal decomposition features
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        features['is_month_start'] = features.index.is_month_start.astype(int)
        features['is_month_end'] = features.index.is_month_end.astype(int)
        features['is_quarter_start'] = features.index.is_quarter_start.astype(int)
        features['is_quarter_end'] = features.index.is_quarter_end.astype(int)

        # Enhanced cyclical encoding
        features['day_of_week_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
        features['day_of_week_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
        features['month_sin'] = np.sin(2 * np.pi * features['month'] / 12)
        features['month_cos'] = np.cos(2 * np.pi * features['month'] / 12)
        features['day_of_year_sin'] = np.sin(2 * np.pi * features['day_of_year'] / 365)
        features['day_of_year_cos'] = np.cos(2 * np.pi * features['day_of_year'] / 365)

        # Volatility regime features
        features['high_volatility_7d'] = (features['volatility_7d'] > features['volatility_7d'].quantile(0.75)).astype(int)
        features['low_volatility_7d'] = (features['volatility_7d'] < features['volatility_7d'].quantile(0.25)).astype(int)
        features['high_volatility_14d'] = (features['volatility_14d'] > features['volatility_14d'].quantile(0.75)).astype(int)
        features['low_volatility_14d'] = (features['volatility_14d'] < features['volatility_14d'].quantile(0.25)).astype(int)
        
        # Spike detection features
        for window in [7, 14, 21]:
            # Detect spikes (values > 2*std above mean)
            mean_val = features[f'cases_{window}d_avg']
            std_val = features[f'volatility_{window}d']
            features[f'spike_{window}d'] = (features['daily_cases'] > (mean_val + 2 * std_val)).astype(int)
            
            # Detect drops (values < 2*std below mean)
            features[f'drop_{window}d'] = (features['daily_cases'] < (mean_val - 2 * std_val)).astype(int)
        
        # Autocorrelation features
        for lag in [1, 7, 14]:
            features[f'autocorr_{lag}d'] = features['daily_cases'].rolling(window=30, min_periods=lag+1).apply(
                lambda x: pd.Series(x).autocorr(lag=lag) if len(x) > lag else 0, raw=True
            ).fillna(0)
        
        # Relative strength index (RSI) - momentum oscillator
        for window in [7, 14]:
            delta = features['daily_cases'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / (loss + 1e-8)
            features[f'rsi_{window}d'] = 100 - (100 / (1 + rs))
            features[f'rsi_{window}d'] = features[f'rsi_{window}d'].fillna(50)
        
        # Moving average convergence divergence (MACD)
        ema_12 = features['daily_cases'].ewm(span=12).mean()
        ema_26 = features['daily_cases'].ewm(span=26).mean()
        features['macd'] = ema_12 - ema_26
        features['macd_signal'] = features['macd'].ewm(span=9).mean()
        features['macd_histogram'] = features['macd'] - features['macd_signal']
        
        # Bollinger Bands
        for window in [20, 30]:
            bb_middle = features['daily_cases'].rolling(window=window).mean()
            bb_std = features['daily_cases'].rolling(window=window).std()
            features[f'bb_upper_{window}d'] = bb_middle + (2 * bb_std)
            features[f'bb_lower_{window}d'] = bb_middle - (2 * bb_std)
            features[f'bb_position_{window}d'] = (features['daily_cases'] - bb_middle) / (2 * bb_std + 1e-8)
        
        # Low-value specific features
        features['is_low_case'] = (features['daily_cases'] <= self.min_cases + 0.1).astype(float)
        features['days_since_high_case'] = features['is_low_case'].groupby((features['is_low_case'] != features['is_low_case'].shift()).cumsum()).cumsum()
        
        # Store feature names
        self.feature_names = features.columns.tolist()
        print(f"✅ Created {len(features.columns)} sophisticated daily features")
        
        # Check for any infinite or NaN values
        if features.isin([np.inf, -np.inf]).any().any():
            print("⚠️ Warning: Infinite values detected. Replacing with finite values.")
            features = features.replace([np.inf, -np.inf], np.nan)
            features = features.fillna(0)
        
        if features.isna().any().any():
            print("⚠️ Warning: NaN values detected. Filling with zeros.")
            features = features.fillna(0)
        
        return features
    
    def prepare_sequences(self, features, target_col='daily_cases'):
        """
        Prepare sequences for LSTM training
        """
        print("🔄 Preparing sequences...")
        
        # Check for data quality before scaling
        print(f"📊 Feature statistics before scaling:")
        print(f"   Mean: {features.mean().mean():.4f}")
        print(f"   Std: {features.std().mean():.4f}")
        print(f"   Min: {features.min().min():.4f}")
        print(f"   Max: {features.max().max():.4f}")
        
        # Scale the features with error handling
        try:
            scaled_data = self.scaler.fit_transform(features)
            print(f"✅ Scaling completed successfully")
        except Exception as e:
            print(f"⚠️ Scaling error: {e}. Using alternative scaling method.")
            # Fallback to simple normalization
            scaled_data = (features - features.mean()) / (features.std() + 1e-8)
        
        X, y = [], []
        
        # Calculate the maximum possible index
        max_start_idx = len(scaled_data) - self.prediction_days - self.sequence_length + 1
        
        if max_start_idx <= 0:
            raise ValueError(
                f"Not enough data points to create sequences. "
                f"Need at least {self.sequence_length + self.prediction_days} points, "
                f"but got {len(scaled_data)}."
            )
        
        # Create sequences
        for i in range(self.sequence_length, len(scaled_data) - self.prediction_days + 1):
            # Input sequence
            X.append(scaled_data[i-self.sequence_length:i])
            # Target (next prediction_days values)
            y.append(scaled_data[i:i+self.prediction_days, features.columns.get_loc(target_col)])
        
        X = np.array(X)
        y = np.array(y)
        
        if len(X) == 0:
            raise ValueError(
                "No sequences could be created. Check your sequence_length and prediction_days parameters."
            )
        
        print(f"📊 Sequences created: X shape {X.shape}, y shape {y.shape}")
        print(f"📊 X range: {X.min():.4f} to {X.max():.4f}")
        print(f"📊 y range: {y.min():.4f} to {y.max():.4f}")
        
        return X, y
    
    def split_data(self, X, y, features):
        """
        Split data into train/validation/test sets using time-based splitting
        Use 60% train, 20% validation, 20% test
        """
        print("✂️ Splitting data using time-based approach...")
        
        # Check if we have enough data
        if len(X) == 0:
            raise ValueError("Not enough data to create sequences. Ensure your dataset has enough records.")
        
        # Get the total number of sequences
        total_sequences = len(X)
        print(f"Total available sequences: {total_sequences}")
        
        if total_sequences < 3:
            # Need at least 3 sequences for train/val/test
            raise ValueError(f"Need at least 3 sequences for splitting, but only got {total_sequences}")
        
        # Calculate split sizes (60% train, 20% validation, 20% test)
        test_size = max(1, int(total_sequences * 0.2))
        val_size = max(1, int(total_sequences * 0.2))
        train_size = total_sequences - test_size - val_size
        
        print(f"Split sizes - Train: {train_size}, Validation: {val_size}, Test: {test_size}")
        
        # Calculate split points
        train_end = train_size
        val_end = train_end + val_size
        
        # Split the data
        X_train = X[:train_end]
        y_train = y[:train_end]
        X_val = X[train_end:val_end]
        y_val = y[train_end:val_end]
        X_test = X[val_end:]
        y_test = y[val_end:]
        
        print(f"📊 Train: {X_train.shape[0]} sequences ({X_train.shape[0] * self.prediction_days} prediction days)")
        print(f"📊 Validation: {X_val.shape[0]} sequences ({X_val.shape[0] * self.prediction_days} prediction days)")
        print(f"📊 Test: {X_test.shape[0]} sequences ({X_test.shape[0] * self.prediction_days} prediction days)")
        
        # Show the date ranges for each split
        try:
            # Get sequence start dates
            sequence_dates = features.index[self.sequence_length:len(features) - self.prediction_days + 1]
            if len(sequence_dates) > 0:
                train_dates = sequence_dates[:train_size]
                val_dates = sequence_dates[train_size:train_size + val_size]
                test_dates = sequence_dates[train_size + val_size:]
                
            if len(train_dates) > 0:
                print(f"📅 Train period: {train_dates[0].strftime('%Y-%m-%d')} to {train_dates[-1].strftime('%Y-%m-%d')}")
            if len(val_dates) > 0:
                print(f"📅 Validation period: {val_dates[0].strftime('%Y-%m-%d')} to {val_dates[-1].strftime('%Y-%m-%d')}")
            if len(test_dates) > 0:
                print(f"📅 Test period: {test_dates[0].strftime('%Y-%m-%d')} to {test_dates[-1].strftime('%Y-%m-%d')}")
            else:
               print("⚠️ Warning: Not enough dates to show period ranges")
        except Exception as e:
            print(f"⚠️ Warning: Could not display date ranges due to: {str(e)}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def build_model(self, input_shape):
        """
        Build enhanced LSTM model with leaky ReLU activation
        """
        print("🏗️ Building enhanced LSTM model...")
        
        model = Sequential([
            # First LSTM Layer with larger units for better pattern recognition
            Bidirectional(LSTM(units=128, return_sequences=True, dropout=0.2, recurrent_dropout=0.2), 
                         input_shape=input_shape),
            # LeakyReLU for better gradient flow with small values
            LeakyReLU(alpha=0.1),
            
            # Second LSTM Layer
            Bidirectional(LSTM(units=64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2)),
            LeakyReLU(alpha=0.1),
            
            # Third LSTM Layer
            Bidirectional(LSTM(units=32, return_sequences=False, dropout=0.2, recurrent_dropout=0.2)),
            LeakyReLU(alpha=0.1),
            
            # Dense layers with LeakyReLU
            Dense(units=100),
            LeakyReLU(alpha=0.1),
            Dropout(0.3),
            
            Dense(units=50),
            LeakyReLU(alpha=0.1),
            Dropout(0.2),
            
            # Output layer (linear activation for regression)
            Dense(units=self.prediction_days)
        ])
        
        # Print model summary
        print("\n📋 Model Summary:")
        model.summary()
        
        # Compile with Huber loss for better handling of outliers
        model.compile(
            optimizer=Adam(learning_rate=0.001, clipnorm=1.0),
            loss=tf.keras.losses.Huber(delta=1.0),  # Huber loss for robustness
            metrics=['mae', 'mse']
        )
        
        return model
    
    def train_model(self, X_train, y_train, X_val, y_val, epochs=300, batch_size=32):
        """
        Train the LSTM model with enhanced callbacks
        """
        print("🎯 Training model...")
        
        # Enhanced callbacks for better training
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=30,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=15,
                min_lr=0.00001,
                verbose=1
            ),
            ModelCheckpoint(
                filepath='best_diabetes_lstm_model_daily.h5',
                monitor='val_loss',
                save_best_only=True,
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
            verbose=1,
            shuffle=True  # Shuffle training data
        )
        
        # Clear memory after training
        gc.collect()
        
        return history
    
    def evaluate_model(self, X_test, y_test, features):
        """
        Evaluate model with enhanced metrics for low values
        """
        print("📊 Evaluating model...")
        
        # Make predictions
        y_pred = self.model.predict(X_test, verbose=0)
        
        # Get the target column index
        target_col_idx = features.columns.get_loc('daily_cases')
        
        # Reshape y_test and y_pred to 1D arrays
        y_test_flat = y_test.flatten()
        y_pred_flat = y_pred.flatten()
        
        # Create dummy arrays for inverse transform
        # Each row should have the same number of columns as the original features
        dummy_test = np.zeros((len(y_test_flat), len(features.columns)))
        dummy_pred = np.zeros((len(y_pred_flat), len(features.columns)))
        
        # Fill in the target column with our actual values
        dummy_test[:, target_col_idx] = y_test_flat
        dummy_pred[:, target_col_idx] = y_pred_flat
        
        # Inverse transform
        y_test_original = self.scaler.inverse_transform(dummy_test)[:, target_col_idx]
        y_pred_original = self.scaler.inverse_transform(dummy_pred)[:, target_col_idx]
        
        # Ensure predictions are at least min_cases
        y_pred_original = np.maximum(y_pred_original, self.min_cases)
        
        # Calculate standard metrics
        mse = mean_squared_error(y_test_original, y_pred_original)
        mae = mean_absolute_error(y_test_original, y_pred_original)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test_original, y_pred_original)
        
        # Calculate MAPE with handling for small values
        mape = np.mean(np.abs((y_test_original - y_pred_original) / (y_test_original + self.min_cases))) * 100
        
        # Calculate metrics for low-value cases
        low_value_mask = y_test_original <= (self.min_cases + 0.1)
        if np.any(low_value_mask):
            low_value_mae = mean_absolute_error(y_test_original[low_value_mask], y_pred_original[low_value_mask])
        else:
            low_value_mae = 0.0
        
        print(f"📊 Test Results:")
        print(f"   MSE: {mse:.2f}")
        print(f"   MAE: {mae:.2f}")
        print(f"   RMSE: {rmse:.2f}")
        print(f"   R² Score: {r2:.4f}")
        print(f"   MAPE: {mape:.2f}%")
        print(f"   Low-value MAE: {low_value_mae:.2f}")
        
        print(f"\n📈 Prediction Analysis:")
        print(f"   Actual range: {y_test_original.min():.2f} - {y_test_original.max():.2f}")
        print(f"   Predicted range: {y_pred_original.min():.2f} - {y_pred_original.max():.2f}")
        
        return y_test_original, y_pred_original, mse, mae, rmse, r2, mape, low_value_mae
    
    def plot_results(self, history, y_test, y_pred, features, save_dir="src/artifacts/lstm_results"):
        """
        Plot training history and predictions with actual dates
        """
        print("📈 Creating plots...")

        # Create output directory
        os.makedirs(save_dir, exist_ok=True)

        # Plot 1: Training History
        plt.figure(figsize=(15, 5))
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss During Training (Daily)')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)

        plt.subplot(1, 2, 2)
        plt.plot(history.history['mae'], label='Training MAE')
        plt.plot(history.history['val_mae'], label='Validation MAE')
        plt.title('Model MAE During Training (Daily)')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{save_dir}/diabetes_lstm_training_history_daily.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 2: Predictions vs Actual with REAL DATES
        plt.figure(figsize=(15, 6))

        # Get the actual dates for the test set
        total_dates = len(features)
        test_start_idx = total_dates - len(y_test) * self.prediction_days
        test_dates = features.index[test_start_idx:test_start_idx + len(y_test) * self.prediction_days]
        
        # Reshape predictions to match dates
        y_test_reshaped = y_test.reshape(-1, self.prediction_days).flatten()
        y_pred_reshaped = y_pred.reshape(-1, self.prediction_days).flatten()
        
        # Plot for first 50 days of test set
        n_days = min(50, len(test_dates))
        plt.plot(test_dates[:n_days], y_test_reshaped[:n_days], label='Actual', alpha=0.7, linewidth=2)
        plt.plot(test_dates[:n_days], y_pred_reshaped[:n_days], label='Predicted', alpha=0.7, linewidth=2)
        plt.title('Diabetes Cases: Actual vs Predicted (Test Set - Daily)')
        plt.xlabel('Day Start Date')
        plt.ylabel('Daily Cases')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{save_dir}/diabetes_lstm_predictions_daily.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 3: Smoothed predictions (4-day rolling average)
        plt.figure(figsize=(15, 6))
        
        # Calculate rolling averages
        y_test_rolling = pd.Series(y_test_reshaped[:n_days]).rolling(window=4, min_periods=1).mean()
        y_pred_rolling = pd.Series(y_pred_reshaped[:n_days]).rolling(window=4, min_periods=1).mean()
        
        plt.plot(test_dates[:n_days], y_test_rolling, label='Actual (Rolling 4d Avg)', alpha=0.7, linewidth=2)
        plt.plot(test_dates[:n_days], y_pred_rolling, label='Predicted (Rolling 4d Avg)', alpha=0.7, linewidth=2)
        plt.title('Diabetes Cases: Actual vs Predicted (Test Set - 4d Rolling Average)')
        plt.xlabel('Day Start Date')
        plt.ylabel('Daily Cases (Rolling 4d Average)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{save_dir}/diabetes_lstm_predictions_smoothed_daily.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Plot 4: Scatter plot
        plt.figure(figsize=(10, 8))
        plt.scatter(y_test, y_pred, alpha=0.6)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual Daily Cases')
        plt.ylabel('Predicted Daily Cases')
        plt.title('Diabetes Cases: Predicted vs Actual (Daily)')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{save_dir}/diabetes_lstm_scatter_daily.png", dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✅ Plots saved to {save_dir}/")
    
    def save_model(self, save_path="src/artifacts/models/diabetes_lstm_model_daily.h5"):
        """
        Save the trained model
        """
        print(f"💾 Saving model to {save_path}...")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save the model
        self.model.save(save_path)
        
        # Save the scaler
        scaler_path = save_path.replace('.h5', '_scaler.pkl')
        import pickle
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"✅ Model and scaler saved successfully!")
    
    def run_full_pipeline(self, data_path="src/artifacts/cleaned_data/weija_diabetes_cleaned.csv"):
        """
        Run the complete LSTM forecasting pipeline
        """
        print("🚀 Starting Diabetes LSTM Forecasting Pipeline (Daily)")
        print("=" * 60)
        
        # Step 1: Load and prepare data
        daily_cases = self.load_and_prepare_data(data_path)
        
        # Step 2: Create features
        features = self.create_features(daily_cases)
        
        # Step 3: Prepare sequences
        X, y = self.prepare_sequences(features)
        
        # Step 4: Split data
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, y, features)
        
        # Step 5: Build model
        self.model = self.build_model(input_shape=(X.shape[1], X.shape[2]))
        
        # Step 6: Train model
        history = self.train_model(X_train, y_train, X_val, y_val)
        
        # Step 7: Evaluate model
        y_test_orig, y_pred_orig, mse, mae, rmse, r2, mape, low_value_mae = self.evaluate_model(X_test, y_test, features)
        
        # Step 8: Plot results
        self.plot_results(history, y_test_orig, y_pred_orig, features)
        
        # Step 9: Save model
        self.save_model()
        
        print("\n" + "=" * 60)
        print("✅ Diabetes LSTM Forecasting Pipeline Completed!")
        print("=" * 60)
        
        return {
            'model': self.model,
            'scaler': self.scaler,
            'metrics': {
                'mse': mse, 'mae': mae, 'rmse': rmse, 'r2': r2, 
                'mape': mape, 'low_value_mae': low_value_mae
            },
            'history': history,
            'y_test': y_test_orig,
            'y_pred': y_pred_orig,
            'features': features
        }

def main():
    """
    Main function to run the diabetes LSTM forecasting with daily aggregation
    """
    # Setup optimizations
    setup_colab()
    
    # Initialize the forecaster with daily approach
    forecaster = DiabetesLSTMForecaster(
        sequence_length=30,  # Look back 30 days
        prediction_days=14,  # Predict next 14 days
        min_cases=1,  # Minimum cases value
        add_noise=True  # Add small noise to minimum values
    )
    
    try:
        # Run the full pipeline
        results = forecaster.run_full_pipeline()
        
        print(f"\n🎯 Final Results:")
        print(f"   MSE: {results['metrics']['mse']:.2f}")
        print(f"   MAE: {results['metrics']['mae']:.2f}")
        print(f"   RMSE: {results['metrics']['rmse']:.2f}")
        print(f"   R² Score: {results['metrics']['r2']:.4f}")
        print(f"   MAPE: {results['metrics']['mape']:.2f}%")
        print(f"   Low-value MAE: {results['metrics'].get('low_value_mae', 0):.2f}")

        print(f"\n✅ Model saved as: best_diabetes_lstm_model_daily.h5")
        print(f"✅ Training completed successfully!")
        
    except ValueError as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTry adjusting the sequence_length and prediction_days parameters based on your data size.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    main()


