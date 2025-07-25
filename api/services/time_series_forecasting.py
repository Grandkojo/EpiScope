import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from django.conf import settings
from typing import Dict, List, Any, Optional
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesForecastingService:
    """Service for time series forecasting of disease data"""
    
    def __init__(self):
        self.diabetes_time_series_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_diabetes_time_stamped.csv')
        self.malaria_time_series_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_malaria_time_stamped.csv')
    
    def get_forecast(self, disease: str, forecast_months: int = 3, locality: str = None) -> Dict[str, Any]:
        """
        Get forecast for specified disease and time period
        
        Args:
            disease: 'diabetes' or 'malaria'
            forecast_months: Number of months to forecast (3, 6, 9, 12)
            locality: Optional locality filter
        """
        try:
            if disease == 'diabetes':
                df = pd.read_csv(self.diabetes_time_series_path)
            elif disease == 'malaria':
                df = pd.read_csv(self.malaria_time_series_path)
            else:
                return {'success': False, 'error': f'Unknown disease: {disease}'}
            
            # Convert Month column to datetime
            df['Month'] = pd.to_datetime(df['Month'])
            
            # Filter by locality if specified
            if locality:
                df = df[df['Address (Locality)'] == locality]
            
            # Group by month and count cases
            monthly_data = df.groupby('Month').size().reset_index(name='cases')
            monthly_data = monthly_data.sort_values('Month')
            
            if len(monthly_data) < 3:
                return {'success': False, 'error': 'Insufficient data for forecasting'}
            
            # Prepare data for forecasting
            forecast_data = self._prepare_forecast_data(monthly_data, forecast_months)
            
            return {
                'success': True,
                'data': {
                    'historical': forecast_data['historical'],
                    'forecast': forecast_data['forecast'],
                    'confidence_intervals': forecast_data['confidence_intervals'],
                    'metadata': {
                        'disease': disease,
                        'forecast_months': forecast_months,
                        'locality': locality,
                        'last_historical_date': forecast_data['last_date'],
                        'forecast_start_date': forecast_data['forecast_start_date']
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_multi_locality_forecast(self, disease: str, forecast_months: int = 3, top_n: int = 5) -> Dict[str, Any]:
        """
        Get forecast for multiple localities
        
        Args:
            disease: 'diabetes' or 'malaria'
            forecast_months: Number of months to forecast
            top_n: Number of top localities to include
        """
        try:
            if disease == 'diabetes':
                df = pd.read_csv(self.diabetes_time_series_path)
            elif disease == 'malaria':
                df = pd.read_csv(self.malaria_time_series_path)
            else:
                return {'success': False, 'error': f'Unknown disease: {disease}'}
            
            # Convert Month column to datetime
            df['Month'] = pd.to_datetime(df['Month'])
            
            # Get top localities by total cases
            top_localities = df['Address (Locality)'].value_counts().head(top_n).index.tolist()
            
            # Filter data for top localities
            filtered_df = df[df['Address (Locality)'].isin(top_localities)]
            
            # Group by month and locality
            locality_data = filtered_df.groupby(['Month', 'Address (Locality)']).size().reset_index(name='cases')
            
            # Pivot to get localities as columns
            locality_pivot = locality_data.pivot(index='Month', columns='Address (Locality)', values='cases').fillna(0)
            
            # Generate forecasts for each locality
            forecasts = {}
            for locality in top_localities:
                if locality in locality_pivot.columns:
                    locality_series = locality_pivot[locality].reset_index()
                    locality_series.columns = ['Month', 'cases']
                    
                    if len(locality_series) >= 3:
                        forecast_data = self._prepare_forecast_data(locality_series, forecast_months)
                        forecasts[locality] = {
                            'historical': forecast_data['historical'],
                            'forecast': forecast_data['forecast'],
                            'confidence_intervals': forecast_data['confidence_intervals']
                        }
            
            return {
                'success': True,
                'data': {
                    'localities': forecasts,
                    'metadata': {
                        'disease': disease,
                        'forecast_months': forecast_months,
                        'top_n': top_n
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_seasonal_forecast(self, disease: str, forecast_months: int = 12) -> Dict[str, Any]:
        """
        Get seasonal forecast with trend and seasonality components
        """
        try:
            if disease == 'diabetes':
                df = pd.read_csv(self.diabetes_time_series_path)
            elif disease == 'malaria':
                df = pd.read_csv(self.malaria_time_series_path)
            else:
                return {'success': False, 'error': f'Unknown disease: {disease}'}
            
            # Convert Month column to datetime
            df['Month'] = pd.to_datetime(df['Month'])
            
            # Group by month and count cases
            monthly_data = df.groupby('Month').size().reset_index(name='cases')
            monthly_data = monthly_data.sort_values('Month')
            
            if len(monthly_data) < 6:
                return {'success': False, 'error': 'Insufficient data for seasonal forecasting'}
            
            # Add seasonal features
            monthly_data['month_num'] = monthly_data['Month'].dt.month
            monthly_data['quarter'] = monthly_data['Month'].dt.quarter
            monthly_data['year'] = monthly_data['Month'].dt.year
            
            # Create seasonal forecast
            seasonal_forecast = self._create_seasonal_forecast(monthly_data, forecast_months)
            
            return {
                'success': True,
                'data': seasonal_forecast
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _prepare_forecast_data(self, monthly_data: pd.DataFrame, forecast_months: int) -> Dict[str, Any]:
        """Prepare data for forecasting"""
        # Create time features
        monthly_data = monthly_data.copy()
        monthly_data['time_index'] = range(len(monthly_data))
        monthly_data['time_index_squared'] = monthly_data['time_index'] ** 2
        
        # Split into features and target
        X = monthly_data[['time_index', 'time_index_squared']].values
        y = monthly_data['cases'].values
        
        # Train linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate future time indices
        last_time_index = monthly_data['time_index'].max()
        future_time_indices = np.arange(last_time_index + 1, last_time_index + 1 + forecast_months)
        future_X = np.column_stack([future_time_indices, future_time_indices ** 2])
        
        # Make predictions
        predictions = model.predict(future_X)
        
        # Calculate confidence intervals (simplified)
        residuals = y - model.predict(X)
        std_residuals = np.std(residuals)
        confidence_intervals = {
            'lower': predictions - 1.96 * std_residuals,
            'upper': predictions + 1.96 * std_residuals
        }
        
        # Prepare historical data
        historical = [
            {
                'date': row['Month'].strftime('%Y-%m'),
                'cases': int(row['cases'])
            }
            for _, row in monthly_data.iterrows()
        ]
        
        # Prepare forecast data
        last_date = monthly_data['Month'].max()
        forecast_dates = [last_date + pd.DateOffset(months=i+1) for i in range(forecast_months)]
        
        forecast = [
            {
                'date': date.strftime('%Y-%m'),
                'cases': int(pred),
                'lower_bound': int(confidence_intervals['lower'][i]),
                'upper_bound': int(confidence_intervals['upper'][i])
            }
            for i, (date, pred) in enumerate(zip(forecast_dates, predictions))
        ]
        
        return {
            'historical': historical,
            'forecast': forecast,
            'confidence_intervals': confidence_intervals,
            'last_date': last_date.strftime('%Y-%m'),
            'forecast_start_date': forecast_dates[0].strftime('%Y-%m')
        }
    
    def _create_seasonal_forecast(self, monthly_data: pd.DataFrame, forecast_months: int) -> Dict[str, Any]:
        """Create seasonal forecast with trend and seasonality"""
        # Calculate seasonal patterns
        seasonal_patterns = monthly_data.groupby('month_num')['cases'].mean()
        
        # Calculate trend
        monthly_data['time_index'] = range(len(monthly_data))
        trend_model = LinearRegression()
        trend_model.fit(monthly_data[['time_index']], monthly_data['cases'])
        
        # Generate future dates
        last_date = monthly_data['Month'].max()
        future_dates = [last_date + pd.DateOffset(months=i+1) for i in range(forecast_months)]
        
        # Generate forecasts
        forecasts = []
        for i, future_date in enumerate(future_dates):
            time_index = len(monthly_data) + i
            trend_component = trend_model.predict([[time_index]])[0]
            seasonal_component = seasonal_patterns.get(future_date.month, seasonal_patterns.mean())
            
            # Combine trend and seasonal components
            forecast_value = max(0, int((trend_component + seasonal_component) / 2))
            
            forecasts.append({
                'date': future_date.strftime('%Y-%m'),
                'cases': forecast_value,
                'trend_component': int(trend_component),
                'seasonal_component': int(seasonal_component)
            })
        
        # Prepare historical data
        historical = [
            {
                'date': row['Month'].strftime('%Y-%m'),
                'cases': int(row['cases'])
            }
            for _, row in monthly_data.iterrows()
        ]
        
        return {
            'historical': historical,
            'forecast': forecasts,
            'seasonal_patterns': {
                month: int(value) for month, value in seasonal_patterns.items()
            },
            'trend_slope': float(trend_model.coef_[0]),
            'metadata': {
                'forecast_months': forecast_months,
                'last_historical_date': last_date.strftime('%Y-%m'),
                'forecast_start_date': future_dates[0].strftime('%Y-%m')
            }
        }
    
    def get_forecast_accuracy_metrics(self, disease: str, test_months: int = 3) -> Dict[str, Any]:
        """Calculate forecast accuracy metrics using historical data"""
        try:
            if disease == 'diabetes':
                df = pd.read_csv(self.diabetes_time_series_path)
            elif disease == 'malaria':
                df = pd.read_csv(self.malaria_time_series_path)
            else:
                return {'success': False, 'error': f'Unknown disease: {disease}'}
            
            # Convert Month column to datetime
            df['Month'] = pd.to_datetime(df['Month'])
            
            # Group by month and count cases
            monthly_data = df.groupby('Month').size().reset_index(name='cases')
            monthly_data = monthly_data.sort_values('Month')
            
            if len(monthly_data) < test_months + 3:
                return {'success': False, 'error': 'Insufficient data for accuracy testing'}
            
            # Split data for testing
            train_data = monthly_data.iloc[:-test_months]
            test_data = monthly_data.iloc[-test_months:]
            
            # Generate forecast for test period
            forecast_data = self._prepare_forecast_data(train_data, test_months)
            
            # Calculate accuracy metrics
            actual_values = test_data['cases'].values
            predicted_values = [f['cases'] for f in forecast_data['forecast']]
            
            # Mean Absolute Error
            mae = np.mean(np.abs(np.array(actual_values) - np.array(predicted_values)))
            
            # Mean Absolute Percentage Error
            mape = np.mean(np.abs((np.array(actual_values) - np.array(predicted_values)) / np.array(actual_values))) * 100
            
            # Root Mean Square Error
            rmse = np.sqrt(np.mean((np.array(actual_values) - np.array(predicted_values)) ** 2))
            
            return {
                'success': True,
                'data': {
                    'mae': float(mae),
                    'mape': float(mape),
                    'rmse': float(rmse),
                    'test_period': test_months,
                    'actual_values': actual_values.tolist(),
                    'predicted_values': predicted_values
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Create singleton instance
forecasting_service = TimeSeriesForecastingService() 