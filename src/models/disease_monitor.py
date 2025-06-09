import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import logging
from datetime import datetime
import joblib
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('disease_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiseaseMonitor:
    def __init__(self):
        self.diabetes_model = None
        self.malaria_model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def preprocess_data(self, df, disease_type):
        """Preprocess the data for model training"""
        logger.info(f"Preprocessing {disease_type} data")
        
        # Create features
        df['Age'] = df['Age'].str.extract(r'(\d+)').astype(float)
        df['Sex'] = df['Sex'].map({'Male': 1, 'Female': 0})
        df['NHIA_Patient'] = df['NHIA Patient'].map({'Yes': 1, 'No': 0})
        df['Pregnant'] = df['Pregnant Patient'].map({'Yes': 1, 'No': 0})
        
        # Extract location features
        df['Location'] = df['Address (Locality)'].fillna('Unknown')
        
        # Create target variable based on disease type
        if disease_type == 'diabetes':
            # For diabetes data, all entries are diabetes cases
            df['Target'] = 1
            # Create synthetic negative cases by duplicating and modifying some entries
            negative_cases = df.sample(n=min(len(df), 100), random_state=42).copy()
            negative_cases['Target'] = 0
            df = pd.concat([df, negative_cases], ignore_index=True)
        else:  # malaria
            # For malaria data, all entries are malaria cases
            df['Target'] = 1
            # Create synthetic negative cases by duplicating and modifying some entries
            negative_cases = df.sample(n=min(len(df), 100), random_state=42).copy()
            negative_cases['Target'] = 0
            df = pd.concat([df, negative_cases], ignore_index=True)
        
        # Select features
        features = ['Age', 'Sex', 'NHIA_Patient', 'Pregnant', 'Location']
        X = df[features].copy()
        y = df['Target']
        
        # Encode categorical variables
        for col in ['Location']:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            X[col] = self.label_encoders[col].fit_transform(X[col])
        
        # Scale numerical features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def train_model(self, diabetes_data, malaria_data):
        """Train models for both diseases"""
        logger.info("Starting model training")
        
        # Train diabetes model
        X_diabetes, y_diabetes = self.preprocess_data(diabetes_data, 'diabetes')
        X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(
            X_diabetes, y_diabetes, test_size=0.2, random_state=42
        )
        
        self.diabetes_model = XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            early_stopping_rounds=10
        )
        
        self.diabetes_model.fit(
            X_train_d, y_train_d,
            eval_set=[(X_test_d, y_test_d)],
            verbose=False
        )
        
        # Train malaria model
        X_malaria, y_malaria = self.preprocess_data(malaria_data, 'malaria')
        X_train_m, X_test_m, y_train_m, y_test_m = train_test_split(
            X_malaria, y_malaria, test_size=0.2, random_state=42
        )
        
        self.malaria_model = XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            early_stopping_rounds=10
        )
        
        self.malaria_model.fit(
            X_train_m, y_train_m,
            eval_set=[(X_test_m, y_test_m)],
            verbose=False
        )
        
        # Log model performance
        self._log_model_performance(X_test_d, y_test_d, X_test_m, y_test_m)
        
    def _log_model_performance(self, X_test_d, y_test_d, X_test_m, y_test_m):
        """Log model performance metrics"""
        # Diabetes model performance
        y_pred_d = self.diabetes_model.predict(X_test_d)
        diabetes_accuracy = accuracy_score(y_test_d, y_pred_d)
        diabetes_report = classification_report(y_test_d, y_pred_d)
        
        # Malaria model performance
        y_pred_m = self.malaria_model.predict(X_test_m)
        malaria_accuracy = accuracy_score(y_test_m, y_pred_m)
        malaria_report = classification_report(y_test_m, y_pred_m)
        
        logger.info(f"Diabetes Model Accuracy: {diabetes_accuracy:.2f}")
        logger.info(f"Diabetes Classification Report:\n{diabetes_report}")
        logger.info(f"Malaria Model Accuracy: {malaria_accuracy:.2f}")
        logger.info(f"Malaria Classification Report:\n{malaria_report}")
    
    def predict(self, data, disease_type):
        """Make predictions for new data"""
        logger.info(f"Making predictions for {disease_type}")
        
        X, _ = self.preprocess_data(data, disease_type)
        model = self.diabetes_model if disease_type == 'diabetes' else self.malaria_model
        
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        
        return predictions, probabilities
    
    def save_models(self, path='models'):
        """Save trained models and encoders"""
        logger.info("Saving models and encoders")
        
        os.makedirs(path, exist_ok=True)
        
        # Save models
        joblib.dump(self.diabetes_model, f'{path}/diabetes_model.joblib')
        joblib.dump(self.malaria_model, f'{path}/malaria_model.joblib')
        
        # Save encoders
        joblib.dump(self.label_encoders, f'{path}/label_encoders.joblib')
        joblib.dump(self.scaler, f'{path}/scaler.joblib')
    
    def load_models(self, path='models'):
        """Load trained models and encoders"""
        logger.info("Loading models and encoders")
        
        self.diabetes_model = joblib.load(f'{path}/diabetes_model.joblib')
        self.malaria_model = joblib.load(f'{path}/malaria_model.joblib')
        self.label_encoders = joblib.load(f'{path}/label_encoders.joblib')
        self.scaler = joblib.load(f'{path}/scaler.joblib') 