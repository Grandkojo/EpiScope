#!/usr/bin/env python3
"""
Model Comparison: LSTM vs ARIMA for Diabetes Forecasting
Comprehensive comparison of both models' performance and usability
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os
import time

# Import our models
from diabetes_lstm_training import DiabetesLSTMForecaster
from diabetes_arima_training import DiabetesARIMAForecaster

# Suppress warnings
warnings.filterwarnings('ignore')

class ModelComparison:
    def __init__(self, data_path="src/artifacts/cleaned_data/weija_diabetes_cleaned.csv"):
        """
        Initialize the model comparison
        """
        self.data_path = data_path
        self.lstm_results = None
        self.arima_results = None
        self.comparison_results = {}
        
    def run_lstm_model(self):
        """
        Run the LSTM model
        """
        print("=" * 60)
        print("🚀 Running LSTM Model")
        print("=" * 60)
        
        start_time = time.time()
        
        # Initialize and run LSTM
        lstm_forecaster = DiabetesLSTMForecaster(
            sequence_length=60,
            prediction_days=14
        )
        
        self.lstm_results = lstm_forecaster.run_full_pipeline(self.data_path)
        
        lstm_time = time.time() - start_time
        print(f"⏱️ LSTM training time: {lstm_time:.2f} seconds")
        
        return self.lstm_results
    
    def run_arima_model(self):
        """
        Run the ARIMA model
        """
        print("=" * 60)
        print("🚀 Running ARIMA Model")
        print("=" * 60)
        
        start_time = time.time()
        
        # Initialize and run ARIMA
        arima_forecaster = DiabetesARIMAForecaster(
            prediction_days=14,
            scaler_type='robust'
        )
        
        self.arima_results = arima_forecaster.run_full_pipeline(self.data_path)
        
        arima_time = time.time() - start_time
        print(f"⏱️ ARIMA training time: {arima_time:.2f} seconds")
        
        return self.arima_results
    
    def compare_metrics(self):
        """
        Compare the metrics between LSTM and ARIMA
        """
        print("=" * 60)
        print("📊 Model Comparison Results")
        print("=" * 60)
        
        if self.lstm_results is None or self.arima_results is None:
            print("❌ Both models must be trained before comparison")
            return
        
        # Extract metrics
        lstm_metrics = self.lstm_results['metrics']
        arima_metrics = self.arima_results['metrics']
        
        # Create comparison table
        comparison_data = {
            'Metric': ['MSE', 'MAE', 'RMSE', 'R² Score', 'MAPE (%)', 'Zero Case Accuracy (%)'],
            'LSTM': [
                f"{lstm_metrics['mse']:.4f}",
                f"{lstm_metrics['mae']:.4f}",
                f"{lstm_metrics['rmse']:.4f}",
                f"{lstm_metrics['r2']:.4f}",
                f"{lstm_metrics['mape']:.2f}",
                f"{lstm_metrics['zero_accuracy']*100:.2f}"
            ],
            'ARIMA': [
                f"{arima_metrics['mse']:.4f}",
                f"{arima_metrics['mae']:.4f}",
                f"{arima_metrics['rmse']:.4f}",
                f"{arima_metrics['r2']:.4f}",
                f"{arima_metrics['mape']:.2f}",
                f"{arima_metrics['zero_accuracy']*100:.2f}"
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        print("\n📋 Metrics Comparison:")
        print(comparison_df.to_string(index=False))
        
        # Determine winner for each metric
        print("\n🏆 Model Performance Analysis:")
        
        # Lower is better metrics
        lower_better = ['MSE', 'MAE', 'RMSE', 'MAPE (%)']
        for metric in lower_better:
            lstm_val = float(lstm_metrics[metric.lower().replace(' (%)', '').replace('²', '2')])
            arima_val = float(arima_metrics[metric.lower().replace(' (%)', '').replace('²', '2')])
            
            if lstm_val < arima_val:
                print(f"   ✅ LSTM wins in {metric}: {lstm_val:.4f} vs {arima_val:.4f}")
            elif arima_val < lstm_val:
                print(f"   ✅ ARIMA wins in {metric}: {arima_val:.4f} vs {lstm_val:.4f}")
            else:
                print(f"   🤝 Tie in {metric}: {lstm_val:.4f}")
        
        # Higher is better metrics
        higher_better = ['R² Score', 'Zero Case Accuracy (%)']
        for metric in higher_better:
            lstm_val = float(lstm_metrics[metric.lower().replace(' (%)', '').replace('²', '2')])
            arima_val = float(arima_metrics[metric.lower().replace(' (%)', '').replace('²', '2')])
            
            if lstm_val > arima_val:
                print(f"   ✅ LSTM wins in {metric}: {lstm_val:.4f} vs {arima_val:.4f}")
            elif arima_val > lstm_val:
                print(f"   ✅ ARIMA wins in {metric}: {arima_val:.4f} vs {lstm_val:.4f}")
            else:
                print(f"   🤝 Tie in {metric}: {lstm_val:.4f}")
        
        # Store comparison results
        self.comparison_results = {
            'comparison_table': comparison_df,
            'lstm_metrics': lstm_metrics,
            'arima_metrics': arima_metrics
        }
        
        return comparison_df
    
    def plot_comparison(self, save_dir="src/artifacts/model_comparison"):
        """
        Create comparison plots
        """
        print("📈 Creating comparison plots...")
        
        # Create output directory
        os.makedirs(save_dir, exist_ok=True)
        
        # Plot 1: Side-by-side predictions comparison
        plt.figure(figsize=(20, 12))
        
        # LSTM predictions
        plt.subplot(2, 2, 1)
        lstm_test_dates = self.lstm_results['features'].index[-len(self.lstm_results['y_test']):]
        plt.plot(lstm_test_dates[:200], self.lstm_results['y_test'][:200], 
                label='Actual', alpha=0.7, linewidth=2)
        plt.plot(lstm_test_dates[:200], self.lstm_results['y_pred'][:200], 
                label='LSTM Predicted', alpha=0.7, linewidth=2)
        plt.title('LSTM Model: Actual vs Predicted')
        plt.xlabel('Date')
        plt.ylabel('Daily Cases')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        
        # ARIMA predictions
        plt.subplot(2, 2, 2)
        arima_test_dates = self.arima_results['test_data'].index
        plt.plot(arima_test_dates, self.arima_results['actual'], 
                label='Actual', alpha=0.7, linewidth=2)
        plt.plot(arima_test_dates, self.arima_results['predicted'], 
                label='ARIMA Predicted', alpha=0.7, linewidth=2)
        plt.title('ARIMA Model: Actual vs Predicted')
        plt.xlabel('Date')
        plt.ylabel('Daily Cases')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        
        # Smoothed comparison
        plt.subplot(2, 2, 3)
        # LSTM smoothed
        lstm_actual_rolling = pd.Series(self.lstm_results['y_test'][:200]).rolling(window=7, min_periods=1).mean()
        lstm_pred_rolling = pd.Series(self.lstm_results['y_pred'][:200]).rolling(window=7, min_periods=1).mean()
        plt.plot(lstm_test_dates[:200], lstm_actual_rolling, 
                label='Actual (7d Avg)', alpha=0.7, linewidth=2)
        plt.plot(lstm_test_dates[:200], lstm_pred_rolling, 
                label='LSTM Predicted (7d Avg)', alpha=0.7, linewidth=2)
        plt.title('LSTM Model: Smoothed Predictions')
        plt.xlabel('Date')
        plt.ylabel('Daily Cases (7d Rolling Average)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        
        # ARIMA smoothed
        plt.subplot(2, 2, 4)
        arima_actual_rolling = pd.Series(self.arima_results['actual']).rolling(window=7, min_periods=1).mean()
        arima_pred_rolling = pd.Series(self.arima_results['predicted']).rolling(window=7, min_periods=1).mean()
        plt.plot(arima_test_dates, arima_actual_rolling, 
                label='Actual (7d Avg)', alpha=0.7, linewidth=2)
        plt.plot(arima_test_dates, arima_pred_rolling, 
                label='ARIMA Predicted (7d Avg)', alpha=0.7, linewidth=2)
        plt.title('ARIMA Model: Smoothed Predictions')
        plt.xlabel('Date')
        plt.ylabel('Daily Cases (7d Rolling Average)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/model_comparison_predictions.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: Metrics comparison bar chart
        plt.figure(figsize=(15, 10))
        
        metrics = ['MSE', 'MAE', 'RMSE', 'R² Score', 'MAPE', 'Zero Accuracy']
        lstm_values = [
            self.lstm_results['metrics']['mse'],
            self.lstm_results['metrics']['mae'],
            self.lstm_results['metrics']['rmse'],
            self.lstm_results['metrics']['r2'],
            self.lstm_results['metrics']['mape'],
            self.lstm_results['metrics']['zero_accuracy']
        ]
        arima_values = [
            self.arima_results['metrics']['mse'],
            self.arima_results['metrics']['mae'],
            self.arima_results['metrics']['rmse'],
            self.arima_results['metrics']['r2'],
            self.arima_results['metrics']['mape'],
            self.arima_results['metrics']['zero_accuracy']
        ]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        plt.bar(x - width/2, lstm_values, width, label='LSTM', alpha=0.8)
        plt.bar(x + width/2, arima_values, width, label='ARIMA', alpha=0.8)
        
        plt.xlabel('Metrics')
        plt.ylabel('Values')
        plt.title('Model Performance Comparison')
        plt.xticks(x, metrics)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, (lstm_val, arima_val) in enumerate(zip(lstm_values, arima_values)):
            plt.text(i - width/2, lstm_val, f'{lstm_val:.3f}', ha='center', va='bottom')
            plt.text(i + width/2, arima_val, f'{arima_val:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/model_comparison_metrics.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 3: Scatter plot comparison
        plt.figure(figsize=(15, 6))
        
        plt.subplot(1, 2, 1)
        plt.scatter(self.lstm_results['y_test'], self.lstm_results['y_pred'], alpha=0.6, label='LSTM')
        plt.plot([0, max(self.lstm_results['y_test'])], [0, max(self.lstm_results['y_test'])], 'r--', lw=2)
        plt.xlabel('Actual Daily Cases')
        plt.ylabel('Predicted Daily Cases')
        plt.title('LSTM: Predicted vs Actual')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.scatter(self.arima_results['actual'], self.arima_results['predicted'], alpha=0.6, label='ARIMA', color='orange')
        plt.plot([0, max(self.arima_results['actual'])], [0, max(self.arima_results['actual'])], 'r--', lw=2)
        plt.xlabel('Actual Daily Cases')
        plt.ylabel('Predicted Daily Cases')
        plt.title('ARIMA: Predicted vs Actual')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f"{save_dir}/model_comparison_scatter.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Comparison plots saved to {save_dir}/")
    
    def provide_recommendations(self):
        """
        Provide recommendations based on the comparison
        """
        print("=" * 60)
        print("💡 Model Recommendations")
        print("=" * 60)
        
        if self.comparison_results == {}:
            print("❌ Run comparison first")
            return
        
        lstm_metrics = self.lstm_results['metrics']
        arima_metrics = self.arima_results['metrics']
        
        # Count wins for each model
        lstm_wins = 0
        arima_wins = 0
        
        # Lower is better metrics
        if lstm_metrics['mse'] < arima_metrics['mse']:
            lstm_wins += 1
        else:
            arima_wins += 1
            
        if lstm_metrics['mae'] < arima_metrics['mae']:
            lstm_wins += 1
        else:
            arima_wins += 1
            
        if lstm_metrics['rmse'] < arima_metrics['rmse']:
            lstm_wins += 1
        else:
            arima_wins += 1
            
        if lstm_metrics['mape'] < arima_metrics['mape']:
            lstm_wins += 1
        else:
            arima_wins += 1
        
        # Higher is better metrics
        if lstm_metrics['r2'] > arima_metrics['r2']:
            lstm_wins += 1
        else:
            arima_wins += 1
            
        if lstm_metrics['zero_accuracy'] > arima_metrics['zero_accuracy']:
            lstm_wins += 1
        else:
            arima_wins += 1
        
        print(f"📊 Overall Performance:")
        print(f"   LSTM wins: {lstm_wins}/6 metrics")
        print(f"   ARIMA wins: {arima_wins}/6 metrics")
        
        print(f"\n🎯 Best Model Recommendation:")
        if lstm_wins > arima_wins:
            print("   🏆 LSTM is the recommended model")
            print("   ✅ Advantages:")
            print("      - Better at capturing complex temporal patterns")
            print("      - Can handle non-linear relationships")
            print("      - More flexible with feature engineering")
            print("   ⚠️ Considerations:")
            print("      - Requires more computational resources")
            print("      - Longer training time")
            print("      - More complex to interpret")
        elif arima_wins > lstm_wins:
            print("   🏆 ARIMA is the recommended model")
            print("   ✅ Advantages:")
            print("      - Faster training and prediction")
            print("      - More interpretable")
            print("      - Requires less computational resources")
            print("      - Good for linear time series patterns")
            print("   ⚠️ Considerations:")
            print("      - Assumes linear relationships")
            print("      - May miss complex patterns")
            print("      - Requires stationary data")
        else:
            print("   🤝 Both models perform similarly")
            print("   💡 Consider using ensemble methods or choosing based on:")
            print("      - Computational constraints")
            print("      - Interpretability requirements")
            print("      - Real-time prediction needs")
        
        print(f"\n🔧 Practical Considerations:")
        print("   📈 For Production Use:")
        if lstm_metrics['mae'] < arima_metrics['mae'] * 0.9:  # LSTM is significantly better
            print("      - Use LSTM if computational resources allow")
            print("      - Consider model serving infrastructure")
        elif arima_metrics['mae'] < lstm_metrics['mae'] * 0.9:  # ARIMA is significantly better
            print("      - Use ARIMA for faster deployment")
            print("      - Easier to maintain and update")
        else:
            print("      - Consider ensemble approach")
            print("      - Choose based on operational constraints")
        
        print("   🎯 For Research/Development:")
        print("      - LSTM offers more flexibility for experimentation")
        print("      - ARIMA provides good baseline performance")
        print("      - Consider both for comprehensive analysis")
    
    def run_full_comparison(self):
        """
        Run the complete comparison pipeline
        """
        print("🚀 Starting Model Comparison Pipeline")
        print("=" * 80)
        
        # Run both models
        self.run_lstm_model()
        self.run_arima_model()
        
        # Compare metrics
        self.compare_metrics()
        
        # Create comparison plots
        self.plot_comparison()
        
        # Provide recommendations
        self.provide_recommendations()
        
        print("\n" + "=" * 80)
        print("✅ Model Comparison Pipeline Completed!")
        print("=" * 80)
        
        return {
            'lstm_results': self.lstm_results,
            'arima_results': self.arima_results,
            'comparison_results': self.comparison_results
        }

def main():
    """
    Main function to run the model comparison
    """
    # Initialize comparison
    comparison = ModelComparison()
    
    # Run full comparison
    results = comparison.run_full_comparison()
    
    print(f"\n📋 Summary:")
    print(f"   LSTM Model: {results['lstm_results']['metrics']}")
    print(f"   ARIMA Model: {results['arima_results']['metrics']}")
    print(f"   Comparison: {results['comparison_results']}")

if __name__ == "__main__":
    main() 