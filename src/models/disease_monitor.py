import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
import shap
import logging
import joblib
import os
import matplotlib.pyplot as plt
from disease_monitor.models import CommonSymptom, Disease
from src.utils.data_preparation import combine_and_label_datasets

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
        self.models = {}
        self.label_encoders = {}
        self.scaler = StandardScaler()

    def preprocess_data(self, df, disease_type, training=True):
        logger.info(f"Preprocessing {disease_type} data")

        df['age'] = df['age'].astype(float)
        df['sex'] = df['sex'].map({'Male': 1, 'Female': 0, 1: 1, 0: 0})
        df['pregnant_patient'] = df['pregnant_patient'].astype(int)
        df['nhia_patient'] = df['nhia_patient'].astype(int)

        df['orgname'] = df['orgname'].fillna('Unknown').astype(str)
        df['address_locality'] = df['address_locality'].replace('', 'Unknown').fillna('Unknown').astype(str)

        disease_obj = Disease.objects.get(disease_name__iexact=disease_type)
        symptom_qs = CommonSymptom.objects.filter(disease=disease_obj).order_by('rank')
        symptoms = list(symptom_qs.values_list('symptom', flat=True))
        ranks = list(symptom_qs.values_list('rank', flat=True))

        for symptom, rank in zip(symptoms, ranks):
            col = f'has_{symptom.lower().replace(" ", "_")}'
            df[col] = df['symptoms'].apply(
                lambda x: int(symptom.lower() in [s.lower() for s in x]) * rank if isinstance(x, list) else 0
            )

        for col in ['orgname', 'address_locality']:
            if training:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                le = self.label_encoders[col]
                df[col] = df[col].apply(lambda x: x if x in le.classes_ else 'Unknown')
                if 'Unknown' not in le.classes_:
                    le.classes_ = np.append(le.classes_, 'Unknown')
                df[col] = le.transform(df[col])

        feature_cols = ['age', 'sex', 'pregnant_patient', 'nhia_patient', 'orgname', 'address_locality'] + \
                       [f'has_{s.lower().replace(" ", "_")}' for s in symptoms]

        X = df[feature_cols].copy()
        y = df['target'] if 'target' in df.columns else None

        num_cols = ['age']
        if training:
            X[num_cols] = self.scaler.fit_transform(X[num_cols])
        else:
            X[num_cols] = self.scaler.transform(X[num_cols])

        return X, y, feature_cols

    def prepare_and_split_data(self, df_pos, df_neg, disease_type, target_col='target', test_size=0.2, val_size=0.1, random_state=42):
        """
        Combine, label, and split data into train/val/test sets.
        Returns: X_train, X_val, X_test, y_train, y_val, y_test, feature_cols
        """
        combined = combine_and_label_datasets(df_pos, df_neg, target_col, disease_type)
        X, y, feature_cols = self.preprocess_data(combined, disease_type, training=True)
        # First split off test set
        X_trainval, X_test, y_trainval, y_test = train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)
        # Then split train/val
        val_relative_size = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(X_trainval, y_trainval, test_size=val_relative_size, stratify=y_trainval, random_state=random_state)
        return X_train, X_val, X_test, y_train, y_val, y_test, feature_cols

    def train_with_validation(self, df_pos, df_neg, disease_type, threshold=0.5):
        """
        Train model with three-way split and probability-based output.
        """
        X_train, X_val, X_test, y_train, y_val, y_test, feature_cols = self.prepare_and_split_data(df_pos, df_neg, disease_type)
        model = XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            early_stopping_rounds=10
        )
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        self.models[disease_type] = model
        self._log_model_performance(model, X_test, y_test, disease_type)
        self._save_shap_summary(model, X_test, feature_cols, disease_type)
        # Store threshold for use in prediction
        self.threshold = threshold
        return model, (X_train, X_val, X_test, y_train, y_val, y_test)

    def generate_shap_explanations(self, df, disease_name, path='models'):
        """Generate and save SHAP summary plot for a trained disease model."""
        logger.info(f"Generating SHAP for {disease_name}")
        
        X, _, _ = self.preprocess_data(df.copy(), disease_name)
        model = self.models.get(disease_name)

        if model is None:
            raise ValueError(f"No trained model found for '{disease_name}'.")

        try:
            print("DEBUG: About to call SHAP summary plot. SHAP version:", shap.__version__)
            explainer = shap.Explainer(model)
            shap_values = explainer(X)

            shap_dir = os.path.join(path, disease_name, 'shap')
            os.makedirs(shap_dir, exist_ok=True)

            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X, show=False)
            plot_path = os.path.join(shap_dir, f'shap_summary_{disease_name}.png')
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close()

            logger.info(f"SHAP summary plot saved to: {plot_path}")
        except Exception as e:
            import traceback
            logger.warning(f"SHAP generation failed for {disease_name}: {e}\n{traceback.format_exc()}")

    def _log_model_performance(self, model, X_test, y_test, disease_name):
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        logger.info(f"{disease_name.title()} Model Accuracy: {accuracy:.2f}")
        logger.info(f"{disease_name.title()} Classification Report:\n{report}")

    def _save_shap_summary(self, model, X, feature_names, disease_name):
        explainer = shap.Explainer(model)
        shap_values = explainer(X)
        shap.summary_plot(shap_values, X, show=False)
        os.makedirs(f'shap_outputs/{disease_name}', exist_ok=True)
        shap.plots.beeswarm(shap_values, show=False)
        shap.summary_plot(shap_values, X, plot_type="bar", show=False)

    def predict(self, data, disease_name):
        X, _, _ = self.preprocess_data(data, disease_name, training=False)
        model = self.models[disease_name]
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)[:, 1]
        return [
            {
                "prediction": int(pred),
                "probability": float(prob)
            }
            for pred, prob in zip(predictions, probabilities)
        ]

    def predict_with_probabilities(self, data, disease_name, threshold=None, uncertain_range=(0.45, 0.55)):
        X, _, _ = self.preprocess_data(data, disease_name, training=False)
        model = self.models[disease_name]
        probabilities = model.predict_proba(X)[:, 1]
        threshold = threshold if threshold is not None else getattr(self, 'threshold', 0.5)
        results = []
        for prob in probabilities:
            if uncertain_range[0] < prob < uncertain_range[1]:
                pred = 'uncertain'
            else:
                pred = int(prob >= threshold)
            results.append({
                'prediction': pred,
                'probability': float(prob)
            })
        return results

    def save_models(self, path='models'):
        os.makedirs(path, exist_ok=True)
        for disease_name, model in self.models.items():
            joblib.dump(model, f'{path}/{disease_name}_model.joblib')
        joblib.dump(self.label_encoders, f'{path}/label_encoders.joblib')
        joblib.dump(self.scaler, f'{path}/scaler.joblib')

    def load_models(self, path='models'):
        for fname in os.listdir(path):
            if fname.endswith('_model.joblib'):
                disease_name = fname.replace('_model.joblib', '')
                self.models[disease_name] = joblib.load(os.path.join(path, fname))
        self.label_encoders = joblib.load(f'{path}/label_encoders.joblib')
        self.scaler = joblib.load(f'{path}/scaler.joblib')
