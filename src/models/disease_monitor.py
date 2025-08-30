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
import re

# Import Vertex AI
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('disease_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OneClassWrapper:
    """Wrapper class for one-class learning models that converts isolation forest scores to probabilities."""
    
    def __init__(self, isolation_model, scaler):
        self.isolation_model = isolation_model
        self.scaler = scaler
        
    def predict_proba(self, X):
        # Get anomaly scores (negative values indicate anomalies)
        scores = self.isolation_model.decision_function(X)
        
        # Convert to probabilities (higher score = more similar to positive cases)
        # Normalize scores to [0, 1] range
        min_score = scores.min()
        max_score = scores.max()
        if max_score > min_score:
            normalized_scores = (scores - min_score) / (max_score - min_score)
        else:
            normalized_scores = np.ones_like(scores) * 0.5
        
        # Return as 2D array with [negative_prob, positive_prob]
        return np.column_stack([1 - normalized_scores, normalized_scores])
    
    def predict(self, X):
        probs = self.predict_proba(X)
        return (probs[:, 1] >= 0.5).astype(int)
    
    # Add __call__ method for SHAP compatibility
    def __call__(self, X):
        return self.predict_proba(X)

class DiseaseMonitor:
    def __init__(self, project_id=None, location="us-central1", model_name="gemini-1.5-pro"):
        self.models = {}
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.vertex_client = None
        self.symptom_models = {}  # Store fine-tuned Vertex AI models for symptom analysis
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        # Initialize Vertex AI if project_id provided
        if project_id and VERTEX_AI_AVAILABLE:
            self._initialize_vertex_ai(project_id, location, model_name)
    
    def _initialize_vertex_ai(self, project_id, location, model_name):
        """Initialize Vertex AI client for symptom analysis."""
        try:
            vertexai.init(project=project_id, location=location)
            self.vertex_client = GenerativeModel(model_name)
            logger.info(f"Vertex AI client initialized successfully with model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI client: {e}")
            self.vertex_client = None

    def extract_disease_code(self, diagnosis_text):
        """Extract disease code from diagnosis text (e.g., E11.65 from 'E11.65 [Type 2 diabetes mellitus with hyperglycemia]')"""
        if pd.isna(diagnosis_text) or diagnosis_text == '':
            return None
        
        # Pattern to match disease codes like E11.65, I10, etc.
        code_pattern = r'([A-Z]\d{2}(?:\.\d+)?)'
        match = re.search(code_pattern, str(diagnosis_text))
        return match.group(1) if match else None

    def preprocess_data(self, df, disease_type, training=True):
        logger.info(f"Preprocessing {disease_type} data")

        # Basic feature preprocessing
        df['age'] = df['age'].astype(float)
        df['sex'] = df['sex'].map({'Male': 1, 'Female': 0, 1: 1, 0: 0})
        df['pregnant_patient'] = df['pregnant_patient'].astype(int)
        df['nhia_patient'] = df['nhia_patient'].astype(int)

        # Handle categorical features
        df['orgname'] = df['orgname'].fillna('Unknown').astype(str)
        df['address_locality'] = df['address_locality'].replace('', 'Unknown').fillna('Unknown').astype(str)

        # Extract disease codes from principal diagnosis (use principal_diagnosis_new field)
        df['disease_code'] = df['principal_diagnosis_new'].apply(self.extract_disease_code)
        df['disease_code'] = df['disease_code'].fillna('Unknown')

        # Encode categorical features
        for col in ['orgname', 'address_locality', 'disease_code']:
            if training:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                le = self.label_encoders[col]
                df[col] = df[col].apply(lambda x: x if x in le.classes_ else 'Unknown')
                if 'Unknown' not in le.classes_:
                    le.classes_ = np.append(le.classes_, 'Unknown')
                df[col] = le.transform(df[col])

        # Core features for the main model (demographic/clinical)
        feature_cols = ['age', 'sex', 'pregnant_patient', 'nhia_patient', 'orgname', 'address_locality', 'disease_code']

        X = df[feature_cols].copy()
        y = df['target'] if 'target' in df.columns else None

        # Scale numerical features
        num_cols = ['age']
        if training:
            X[num_cols] = self.scaler.fit_transform(X[num_cols])
        else:
            X[num_cols] = self.scaler.transform(X[num_cols])

        return X, y, feature_cols

    def analyze_symptoms_with_vertex_ai(self, symptoms_text, disease_name):
        """
        Analyze symptoms using Vertex AI model and return a risk score.
        
        Args:
            symptoms_text (str): User-provided symptoms (text or structured)
            disease_name (str): Name of the disease to analyze for
            
        Returns:
            float: Risk score between 0 and 1
        """
        if not self.vertex_client:
            logger.warning("Vertex AI client not available, returning default score")
            return 0.5
        
        try:
            # Get disease-specific symptoms from database
            disease_obj = Disease.objects.get(disease_name__iexact=disease_name)
            symptom_qs = CommonSymptom.objects.filter(disease=disease_obj).order_by('rank')
            expected_symptoms = list(symptom_qs.values_list('symptom', flat=True))
            
            prompt = f"""
            Analyze the following symptoms for {disease_name} risk assessment.
            
            Patient symptoms: {symptoms_text}
            
            Expected symptoms for {disease_name}: {', '.join(expected_symptoms)}
            
            Please provide a risk score between 0 and 1 where:
            - 0.0-0.2: Very low risk (symptoms completely unrelated to {disease_name})
            - 0.2-0.4: Low risk (some symptoms might be vaguely related but not specific)
            - 0.4-0.6: Moderate risk (some symptoms match but not strongly)
            - 0.6-0.8: High risk (strong symptom match)
            - 0.8-1.0: Very high risk (classic {disease_name} symptoms)
            
            IMPORTANT GUIDELINES:
            1. Be very strict about symptom relevance
            2. If symptoms are completely unrelated (like cough for diabetes), score 0.0-0.2
            3. Only score higher if symptoms are specifically associated with {disease_name}
            4. Consider symptom severity, frequency, and combination patterns
            5. If symptoms contradict {disease_name} patterns, score very low
            
            Return only the numerical score (e.g., 0.15).
            """
            
            response = self.vertex_client.generate_content(prompt)
            score_text = response.text.strip()
            
            # Extract numerical score
            score_match = re.search(r'0\.\d+|\d+\.\d+', score_text)
            if score_match:
                score = float(score_match.group())
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            else:
                logger.warning(f"Could not extract score from Vertex AI response: {score_text}")
                return 0.5
                
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            return 0.5

    def generate_negative_cases(self, df, disease_name, n_negative=None):
        """
        Generate negative cases for training by sampling cases that don't contain the disease name.
        
        Args:
            df: Full dataset
            disease_name: Name of the disease to exclude
            n_negative: Number of negative cases to generate (default: same as positive cases)
            
        Returns:
            DataFrame with negative cases
        """
        # Filter out cases that contain the disease name
        negative_mask = ~df['principal_diagnosis_new'].str.contains(disease_name, case=False, na=False)
        negative_cases = df[negative_mask].copy()
        
        # If no n_negative specified, use same number as positive cases
        if n_negative is None:
            positive_count = len(df[df['principal_diagnosis_new'].str.contains(disease_name, case=False, na=False)])
            n_negative = positive_count
        
        # Sample negative cases, ensuring we don't exceed available cases
        n_negative = min(n_negative, len(negative_cases))
        
        if n_negative == 0:
            logger.warning(f"No negative cases available for {disease_name}")
            return pd.DataFrame()
        
        # Random sample with stratification if possible
        try:
            # Try to maintain demographic balance by sampling from different age groups
            negative_cases['age_group'] = pd.cut(negative_cases['age'], bins=5, labels=['0-20', '21-40', '41-60', '61-80', '80+'])
            negative_sample = negative_cases.groupby('age_group', group_keys=False).apply(
                lambda x: x.sample(min(len(x), n_negative // 5 + 1))
            ).head(n_negative)
        except:
            # Fallback to simple random sampling
            negative_sample = negative_cases.sample(n=n_negative, random_state=42)
        
        # Add target column (0 for negative cases)
        negative_sample['target'] = 0
        
        logger.info(f"Generated {len(negative_sample)} negative cases for {disease_name}")
        return negative_sample

    def train_with_cross_validation(self, df_pos, df_neg, disease_type, threshold=0.7, cv_folds=5):
        """
        Train a robust XGBoost model with cross-validation and both positive/negative cases.
        
        Args:
            df_pos: Positive cases DataFrame
            df_neg: Negative cases DataFrame  
            disease_type: Name of the disease
            threshold: Classification threshold (default: 0.7 for conservative medical predictions)
            cv_folds: Number of cross-validation folds
            
        Returns:
            Trained model and cross-validation results
        """
        from sklearn.model_selection import StratifiedKFold, cross_val_score
        from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score, roc_auc_score
        import xgboost as xgb
        
        # Combine positive and negative cases
        df_pos['target'] = 1
        df_neg['target'] = 0
        
        # Ensure we have both positive and negative cases
        if len(df_pos) == 0:
            raise ValueError(f"No positive cases found for {disease_type}")
        if len(df_neg) == 0:
            logger.warning(f"No negative cases found for {disease_type}, using only positive cases")
            combined_df = df_pos
        else:
            combined_df = pd.concat([df_pos, df_neg], ignore_index=True)
        
        logger.info(f"Training {disease_type} model with {len(df_pos)} positive and {len(df_neg)} negative cases")
        
        # Preprocess the data
        X, y, feature_cols = self.preprocess_data(combined_df, disease_type, training=True)
        
        # Initialize XGBoost model with optimized parameters
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        
        # Set up cross-validation
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        
        # Define scoring metrics
        scoring = {
            'precision': make_scorer(precision_score),
            'recall': make_scorer(recall_score),
            'f1': make_scorer(f1_score),
            'roc_auc': make_scorer(roc_auc_score, needs_proba=True)
        }
        
        # Perform cross-validation
        cv_results = {}
        for metric_name, scorer in scoring.items():
            scores = cross_val_score(model, X, y, cv=skf, scoring=scorer)
            cv_results[metric_name] = {
                'mean': scores.mean(),
                'std': scores.std(),
                'scores': scores
            }
            logger.info(f"{disease_type} CV {metric_name}: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
        
        # Train final model on full dataset
        model.fit(X, y)
        
        # Store the model
        self.models[disease_type] = model
        
        # Store threshold for use in prediction (default to 0.7 for conservative medical predictions)
        self.threshold = threshold
        
        # Generate SHAP explanations
        self._save_shap_summary(model, X, feature_cols, disease_type)
        
        return model, cv_results

    def train_with_validation(self, df_pos, df_neg, disease_type, threshold=0.7):
        """
        Train a robust XGBoost model with both positive and negative cases.
        This replaces the old one-class learning approach.
        """
        # Generate negative cases if not provided
        if df_neg is None or len(df_neg) == 0:
            df_neg = self.generate_negative_cases(df_pos, disease_type)
        
        # Use the new cross-validation training method
        model, cv_results = self.train_with_cross_validation(df_pos, df_neg, disease_type, threshold)
        
        # For backward compatibility, return a tuple similar to the old method
        # Split data for final evaluation
        from sklearn.model_selection import train_test_split
        X, y, _ = self.preprocess_data(pd.concat([df_pos, df_neg], ignore_index=True), disease_type, training=False)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        return model, (X_train, X_test, y_train, y_test)

    def generate_shap_explanations(self, df, disease_name, path='models'):
        """Generate and save SHAP summary plot for a trained disease model."""
        logger.info(f"Generating SHAP for {disease_name}")
        
        X, _, _ = self.preprocess_data(df.copy(), disease_name)
        model = self.models.get(disease_name)

        if model is None:
            raise ValueError(f"No trained model found for '{disease_name}'.")

        try:
            print("DEBUG: About to call SHAP summary plot. SHAP version:", shap.__version__)
            # Use background data (X) as masker to avoid "masker cannot be None" error
            explainer = shap.Explainer(model, X)
            shap_values = explainer(X)

            shap_dir = os.path.join(path, disease_name, 'shap')
            os.makedirs(shap_dir, exist_ok=True)

            # Generate summary plot using beeswarm plot (shows all features)
            plt.figure(figsize=(12, 8))
            # Use beeswarm plot which is more reliable for showing all features
            shap.plots.beeswarm(shap_values, show=False)
            plot_path = os.path.join(shap_dir, f'shap_summary_{disease_name}.png')
            plt.savefig(plot_path, bbox_inches='tight', dpi=300)
            plt.close()
            logger.info(f"SHAP summary plot saved to: {plot_path}")

            # Generate bar plot (feature importance ranking)
            plt.figure(figsize=(10, 6))
            shap.plots.bar(shap_values, show=False)
            bar_path = os.path.join(shap_dir, f'shap_bar_{disease_name}.png')
            plt.savefig(bar_path, bbox_inches='tight', dpi=300)
            plt.close()
            logger.info(f"SHAP bar plot saved to: {bar_path}")

            # Generate interaction plot for key features (if we have enough features)
            if X.shape[1] >= 2:
                try:
                    # Select top 4 most important features for interaction analysis
                    feature_importance = np.abs(shap_values.values).mean(0)
                    top_features_idx = np.argsort(feature_importance)[-4:]
                    top_features = X.columns[top_features_idx]
                    
                    plt.figure(figsize=(12, 10))
                    shap.plots.interaction(shap_values, show=False)
                    interaction_path = os.path.join(shap_dir, f'shap_interaction_{disease_name}.png')
                    plt.savefig(interaction_path, bbox_inches='tight', dpi=300)
                    plt.close()
                    logger.info(f"SHAP interaction plot saved to: {interaction_path}")
                except Exception as e:
                    logger.warning(f"SHAP interaction plot failed for {disease_name}: {e}")

            # Generate waterfall plot for a sample case
            try:
                plt.figure(figsize=(10, 8))
                shap.plots.waterfall(shap_values[0], show=False)
                waterfall_path = os.path.join(shap_dir, f'shap_waterfall_{disease_name}.png')
                plt.savefig(waterfall_path, bbox_inches='tight', dpi=300)
                plt.close()
                logger.info(f"SHAP waterfall plot saved to: {waterfall_path}")
            except Exception as e:
                logger.warning(f"SHAP waterfall plot failed for {disease_name}: {e}")

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
        """Generate SHAP summary plot for the model."""
        try:
            # Check if model is compatible with SHAP
            if hasattr(model, '__call__') or hasattr(model, 'predict_proba'):
                explainer = shap.Explainer(model, X)
                shap_values = explainer(X)
                
                # Create directory for SHAP outputs
                shap_dir = f'shap_outputs/{disease_name}'
                os.makedirs(shap_dir, exist_ok=True)
                
                # Generate summary plot using beeswarm plot (shows all features)
                plt.figure(figsize=(12, 8))
                # Use beeswarm plot which is more reliable for showing all features
                shap.plots.beeswarm(shap_values, show=False)
                plt.savefig(f'{shap_dir}/shap_summary_{disease_name}.png', bbox_inches='tight', dpi=300)
                plt.close()
                
                # Generate bar plot (feature importance ranking)
                plt.figure(figsize=(10, 6))
                shap.plots.bar(shap_values, show=False)
                plt.savefig(f'{shap_dir}/shap_bar_{disease_name}.png', bbox_inches='tight', dpi=300)
                plt.close()
                
                # Generate interaction plot for key features (if we have enough features)
                if X.shape[1] >= 2:
                    try:
                        # Select top 4 most important features for interaction analysis
                        feature_importance = np.abs(shap_values.values).mean(0)
                        top_features_idx = np.argsort(feature_importance)[-4:]
                        top_features = X.columns[top_features_idx]
                        
                        plt.figure(figsize=(12, 10))
                        shap.plots.interaction(shap_values, show=False)
                        plt.savefig(f'{shap_dir}/shap_interaction_{disease_name}.png', 
                                  bbox_inches='tight', dpi=300)
                        plt.close()
                    except Exception as e:
                        logger.warning(f"SHAP interaction plot failed for {disease_name}: {e}")
                
                # Generate waterfall plot for a sample case
                try:
                    plt.figure(figsize=(10, 8))
                    shap.plots.waterfall(shap_values[0], show=False)
                    plt.savefig(f'{shap_dir}/shap_waterfall_{disease_name}.png', 
                              bbox_inches='tight', dpi=300)
                    plt.close()
                except Exception as e:
                    logger.warning(f"SHAP waterfall plot failed for {disease_name}: {e}")
                
                logger.info(f"SHAP plots saved for {disease_name}")
            else:
                logger.warning(f"Model for {disease_name} is not compatible with SHAP, skipping SHAP generation")
        except Exception as e:
            logger.warning(f"SHAP generation failed for {disease_name}: {e}")
            # Continue without SHAP - it's not critical for model functionality

    def predict(self, data, disease_name, symptoms_text=None):
        """
        Predict disease probability using demographic/clinical features and Vertex AI symptom analysis.
        
        Args:
            data: Patient demographic/clinical data
            disease_name: Name of the disease
            symptoms_text: Optional symptoms text for Vertex AI analysis
            
        Returns:
            List of prediction dictionaries with combined scores
        """
        # Get base prediction from XGBoost model
        X, _, _ = self.preprocess_data(data, disease_name, training=False)
        model = self.models[disease_name]
        
        # Get baseline confidence from XGBoost model
        base_probabilities = model.predict_proba(X)[:, 1]
        
        results = []
        for i, base_prob in enumerate(base_probabilities):
            result = {
                "base_probability": float(base_prob),
                "symptom_score": None,
                "combined_probability": float(base_prob),
                "prediction": int(base_prob >= getattr(self, 'threshold', 0.7))
            }
            
            # Add symptom analysis if provided
            if symptoms_text:
                symptom_score = self.analyze_symptoms_with_vertex_ai(symptoms_text, disease_name)
                result["symptom_score"] = symptom_score
                
                # Dynamic weighting based on symptom relevance
                # If symptoms strongly contradict base prediction, give more weight to symptoms
                base_pred = 1 if base_prob >= 0.7 else 0  # Use 0.7 threshold for base prediction
                symptom_pred = 1 if symptom_score >= 0.5 else 0
                
                if base_pred != symptom_pred:
                    # Contradiction detected - give more weight to symptoms
                    symptom_weight = 0.7
                    base_weight = 0.3
                else:
                    # Agreement - use balanced weights
                    symptom_weight = 0.5
                    base_weight = 0.5
                
                # Combine scores with dynamic weighting
                combined_prob = base_weight * base_prob + symptom_weight * symptom_score
                result["combined_probability"] = float(combined_prob)
                
                # Dynamic threshold based on symptom relevance
                # If symptoms are very low, require higher base probability
                if symptom_score < 0.3:
                    dynamic_threshold = 0.8  # Require very high confidence
                elif symptom_score < 0.5:
                    dynamic_threshold = 0.75  # Require high confidence
                else:
                    dynamic_threshold = getattr(self, 'threshold', 0.7)
                
                result["prediction"] = int(combined_prob >= dynamic_threshold)
                result["dynamic_threshold"] = dynamic_threshold
            
            results.append(result)
        
        return results

    def predict_with_probabilities(self, data, disease_name, symptoms_text=None, threshold=None, uncertain_range=(0.45, 0.55)):
        """
        Enhanced prediction with uncertainty handling and symptom integration.
        """
        predictions = self.predict(data, disease_name, symptoms_text)
        threshold = threshold if threshold is not None else getattr(self, 'threshold', 0.7)
        
        for result in predictions:
            prob = result['combined_probability']
            base_prob = result['base_probability']
            symptom_score = result.get('symptom_score')
            
            # Enhanced uncertainty detection
            is_uncertain = False
            
            # Check if symptoms contradict base model significantly
            if symptom_score is not None:
                base_pred = 1 if base_prob >= 0.7 else 0  # Use 0.7 threshold
                symptom_pred = 1 if symptom_score >= 0.5 else 0
                
                # If there's a contradiction and symptoms are very low
                if base_pred != symptom_pred and symptom_score < 0.3:
                    is_uncertain = True
                    result['uncertainty_reason'] = 'symptom_contradiction'
                
                # If combined probability is in uncertain range
                elif uncertain_range[0] < prob < uncertain_range[1]:
                    is_uncertain = True
                    result['uncertainty_reason'] = 'borderline_probability'
                
                # If base model is very confident but symptoms disagree
                elif (base_prob > 0.8 and symptom_score < 0.4) or (base_prob < 0.3 and symptom_score > 0.6):
                    is_uncertain = True
                    result['uncertainty_reason'] = 'model_disagreement'
            
            if is_uncertain:
                result['prediction'] = 'uncertain'
            else:
                result['prediction'] = int(prob >= threshold)
        
        return predictions

    def save_models(self, path='models'):
        os.makedirs(path, exist_ok=True)
        for disease_name, model in self.models.items():
            joblib.dump(model, f'{path}/{disease_name}_model.joblib')
        joblib.dump(self.label_encoders, f'{path}/label_encoders.joblib')
        joblib.dump(self.scaler, f'{path}/scaler.joblib')

    def load_models(self, path='models'):
        # Load v2 models (.pkl files)
        for fname in os.listdir(path):
            if fname.endswith('_xgboost_model_v2.pkl'):
                disease_name = fname.replace('_xgboost_model_v2.pkl', '')
                import pickle
                with open(os.path.join(path, fname), 'rb') as f:
                    self.models[disease_name] = pickle.load(f)
        
        # For v2 models, we don't need label encoders or scalers as they use direct feature engineering
        # Initialize empty encoders and scaler for compatibility
        from sklearn.preprocessing import LabelEncoder, StandardScaler
        self.label_encoders = {}
        self.scaler = StandardScaler()

    def predict_with_new_models(self, data, disease_name, symptoms_text=None, cost_optional=True):
        """
        Predict using v2 models with enhanced feature engineering.
        
        Args:
            data: Patient demographic/clinical data (DataFrame)
            disease_name: Name of the disease
            symptoms_text: Optional symptoms text for Vertex AI analysis
            cost_optional: Whether cost data is optional
            
        Returns:
            List of prediction dictionaries with enhanced features
        """
        if disease_name not in self.models:
            raise ValueError(f"Model for {disease_name} not found")
        
        # Prepare data using v2 feature engineering
        df_processed = self._prepare_v2_features(data, disease_name, cost_optional)
        
        # Get model predictions
        model = self.models[disease_name]
        base_probabilities = model.predict_proba(df_processed)[:, 1]
        
        results = []
        for i, base_prob in enumerate(base_probabilities):
            result = {
                "base_probability": float(base_prob),
                "symptom_score": None,
                "combined_probability": float(base_prob),
                "prediction": int(base_prob >= 0.7),  # Default threshold for v2 models
                "locality": data.iloc[i]['Locality'] if 'Locality' in data.columns else None,
                "cost_included": cost_optional and 'Cost of Treatment (GHS )' in data.columns,
                "features_used": list(df_processed.columns)
            }
            
            # Add symptom analysis if provided
            if symptoms_text and self.vertex_client:
                symptom_score = self.analyze_symptoms_with_vertex_ai(symptoms_text, disease_name)
                result["symptom_score"] = symptom_score
                
                # Enhanced weighting for v2 models
                if symptom_score is not None:
                    # Dynamic weighting based on symptom relevance
                    base_pred = 1 if base_prob >= 0.7 else 0
                    symptom_pred = 1 if symptom_score >= 0.5 else 0
                    
                    if base_pred != symptom_pred:
                        # Contradiction - give more weight to symptoms
                        symptom_weight = 0.7
                        base_weight = 0.3
                    else:
                        # Agreement - balanced weights
                        symptom_weight = 0.5
                        base_weight = 0.5
                    
                    # Combine scores
                    combined_prob = base_weight * base_prob + symptom_weight * symptom_score
                    result["combined_probability"] = float(combined_prob)
                    
                    # Dynamic threshold
                    if symptom_score < 0.3:
                        dynamic_threshold = 0.8
                    elif symptom_score < 0.5:
                        dynamic_threshold = 0.75
                    else:
                        dynamic_threshold = 0.7
                    
                    result["prediction"] = int(combined_prob >= dynamic_threshold)
                    result["dynamic_threshold"] = dynamic_threshold
            
            results.append(result)
        
        return results

    def _prepare_v2_features(self, data, disease_type, cost_optional=True):
        """
        Prepare features for v2 models using the same feature engineering as training.
        """
        import re
        from datetime import datetime
        
        # Define medication dictionaries (same as training)
        DIABETES_MEDICATIONS = [
            'metformin', 'insulin', 'glibenclamide', 'pioglitazone', 'glimeperide',
            'gliclazide', 'sitagliptin', 'linagliptin', 'empagliflozin', 'dapagliflozin',
            'canagliflozin', 'acarbose', 'miglitol', 'repaglinide', 'nateglinide'
        ]
        
        MALARIA_MEDICATIONS = [
            'artemether', 'lumefantrine', 'artesunate', 'coartem', 'lonart',
            'artemether+lumefantrine', 'artemether+lumefan', 'artesunate injection',
            'artemether injection', 'quinine', 'chloroquine', 'mefloquine',
            'doxycycline', 'primaquine', 'atovaquone', 'proguanil'
        ]
        
        def extract_age_numeric(age_input):
            if pd.isna(age_input) or age_input == '':
                return 30  # Default age
            if isinstance(age_input, (int, float)):
                return int(age_input)
            age_str = str(age_input)
            numbers = re.findall(r'\d+', age_str)
            return int(numbers[0]) if numbers else 30
        
        def extract_temporal_features(date_str):
            try:
                date = pd.to_datetime(date_str)
                return {
                    'month': date.month,
                    'year': date.year,
                    'day_of_week': date.dayofweek,
                    'season': (date.month % 12 + 3) // 3,
                    'is_weekend': 1 if date.dayofweek >= 5 else 0
                }
            except:
                return {'month': 1, 'year': 2022, 'day_of_week': 0, 'season': 1, 'is_weekend': 0}
        
        def check_medication_presence(medicine_str, medication_list):
            if pd.isna(medicine_str) or medicine_str == '':
                return 0
            medicine_lower = medicine_str.lower()
            for med in medication_list:
                if med.lower() in medicine_lower:
                    return 1
            return 0
        
        def count_medications(medicine_str):
            if pd.isna(medicine_str) or medicine_str == '':
                return 0
            medicine_count = len(re.findall(r'\[.*?\]', medicine_str))
            return medicine_count
        
        # Create a copy of the data
        df = data.copy()
        
        # Extract age features
        df['age_numeric'] = df['Age'].apply(extract_age_numeric)
        
        # Extract temporal features
        temporal_features = df['Schedule Date'].apply(extract_temporal_features)
        df['month'] = temporal_features.apply(lambda x: x['month'])
        df['year'] = temporal_features.apply(lambda x: x['year'])
        df['day_of_week'] = temporal_features.apply(lambda x: x['day_of_week'])
        df['season'] = temporal_features.apply(lambda x: x['season'])
        df['is_weekend'] = temporal_features.apply(lambda x: x['is_weekend'])
        
        # Medication features
        df['diabetes_medication_present'] = df['Medicine Prescribed'].apply(
            lambda x: check_medication_presence(x, DIABETES_MEDICATIONS)
        )
        df['malaria_medication_present'] = df['Medicine Prescribed'].apply(
            lambda x: check_medication_presence(x, MALARIA_MEDICATIONS)
        )
        
        # General medication features
        df['medication_count'] = df['Medicine Prescribed'].apply(count_medications)
        df['has_medication'] = (df['medication_count'] > 0).astype(int)
        
        # Binary encoding for categorical variables
        df['is_pregnant'] = (df['Pregnant Patient'].astype(str).str.lower() == 'yes').astype(int)
        df['is_insured'] = (df['NHIA Patient'].astype(str).str.lower() == 'insured').astype(int)
        df['is_male'] = (df['Gender'].astype(str).str.lower() == 'male').astype(int)
        
        # Locality features
        df['locality_encoded'] = df['Locality'].astype(str).apply(lambda x: hash(x) % 100)
        
        # Cost features
        if 'Cost of Treatment (GHS )' in df.columns and cost_optional:
            df['Cost of Treatment (GHS )'] = pd.to_numeric(df['Cost of Treatment (GHS )'], errors='coerce')
            df['has_cost'] = (df['Cost of Treatment (GHS )'] > 0).astype(int)
            df['cost_category'] = pd.cut(
                df['Cost of Treatment (GHS )'], 
                bins=[0, 10, 50, 100, float('inf')], 
                labels=[0, 1, 2, 3]
            ).fillna(0).astype(int)
        else:
            df['has_cost'] = 0
            df['cost_category'] = 0
        
        # Select features for the model (same as training)
        feature_columns = [
            'age_numeric', 'is_male', 'is_pregnant', 'is_insured',
            'month', 'year', 'day_of_week', 'season', 'is_weekend',
            'medication_count', 'has_medication',
            'locality_encoded',
            f'{disease_type}_medication_present',
            'has_cost', 'cost_category'
        ]
        
        # Ensure all required features exist
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        return df[feature_columns]

    def analyze_chat_message(self, user_message):
        """
        Analyze user chat message and generate contextual response using Vertex AI.
        
        Args:
            user_message (str): User's chat message
            
        Returns:
            str: Contextual response based on disease monitoring data
        """
        if not self.vertex_client:
            return "I'm sorry, but the AI system is not available at the moment."
        
        try:
            # Detect disease focus from user message
            disease_focus = self._detect_disease_focus(user_message)
            
            # Get relevant disease data
            disease_data = self._get_disease_data(disease_focus)
            
            # Create contextual prompt
            prompt = self._create_chat_prompt(user_message, disease_focus, disease_data)
            
            # Get response from Vertex AI
            response = self.vertex_client.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error in chat analysis: {e}")
            return "I apologize, but I encountered an error while processing your request."

    def _detect_disease_focus(self, user_message):
        """Detect which disease the user is asking about"""
        user_message_lower = user_message.lower()
        
        if 'diabetes' in user_message_lower or 'diabetic' in user_message_lower:
            return 'diabetes'
        elif 'malaria' in user_message_lower:
            return 'malaria'
        elif 'cholera' in user_message_lower:
            return 'cholera'
        elif 'meningitis' in user_message_lower:
            return 'meningitis'
        else:
            return 'general'

    def _get_disease_data(self, disease_focus):
        """Get relevant disease data for context"""
        try:
            from disease_monitor.models import Disease, HospitalHealthData
            
            if disease_focus == 'general':
                return {
                    'total_cases': HospitalHealthData.objects.count(),
                    'diseases': list(Disease.objects.values_list('disease_name', flat=True))
                }
            
            # Get disease-specific data
            disease_obj = Disease.objects.filter(disease_name__iexact=disease_focus).first()
            if not disease_obj:
                return {}
            
            # Get case count
            case_count = HospitalHealthData.objects.filter(
                principal_diagnosis_new__icontains=disease_focus
            ).count()
            
            # Get recent trends (last 30 days)
            from django.utils import timezone
            from datetime import timedelta
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            recent_cases = HospitalHealthData.objects.filter(
                principal_diagnosis_new__icontains=disease_focus,
                created_at__gte=thirty_days_ago
            ).count()
            
            return {
                'disease_name': disease_obj.disease_name,
                'total_cases': case_count,
                'recent_cases': recent_cases,
                'description': disease_obj.description if hasattr(disease_obj, 'description') else '',
                'symptoms': list(disease_obj.commonsymptom_set.values_list('symptom', flat=True))
            }
            
        except Exception as e:
            logger.error(f"Error getting disease data: {e}")
            return {}

    def _create_chat_prompt(self, user_message, disease_focus, disease_data):
        """Create contextual prompt for Vertex AI"""
        
        base_prompt = f"""
        You are EpiScope Health AI, a specialized assistant for epidemic monitoring and disease analysis.
        
        User Question: {user_message}
        
        Context Information:
        """
        
        if disease_focus == 'general':
            prompt = base_prompt + f"""
            - Total cases in system: {disease_data.get('total_cases', 0)}
            - Available diseases: {', '.join(disease_data.get('diseases', []))}
            
            Please provide a helpful response about epidemic monitoring, focusing on:
            1. General health trends and monitoring
            2. Available disease data and insights
            3. How to interpret health metrics
            4. Best practices for disease prevention
            
            Be informative, professional, and encouraging. Use medical terminology appropriately.
            """
        else:
            disease_info = disease_data.get('disease_name', disease_focus)
            total_cases = disease_data.get('total_cases', 0)
            recent_cases = disease_data.get('recent_cases', 0)
            symptoms = disease_data.get('symptoms', [])
            
            prompt = base_prompt + f"""
            Disease Focus: {disease_info}
            - Total cases: {total_cases}
            - Recent cases (30 days): {recent_cases}
            - Common symptoms: {', '.join(symptoms) if symptoms else 'Not specified'}
            
            Please provide a comprehensive response about {disease_info} that includes:
            1. Current trends and patterns
            2. Key risk factors and prevention strategies
            3. Monitoring and early detection methods
            4. When to seek medical attention
            
            If the user is asking about trends, focus on the data insights.
            If asking about symptoms, provide detailed symptom analysis.
            If asking about prevention, give practical advice.
            
            Be professional, accurate, and helpful. Always encourage consulting healthcare professionals for medical advice.
            """
        
        return prompt

    def generate_fine_tuning_data(self, chat_history, disease_name=None):
        """
        Generate fine-tuning data from chat history.
        
        Args:
            chat_history: List of chat messages
            disease_name: Optional disease filter
            
        Returns:
            List of training examples for Vertex AI fine-tuning
        """
        training_data = []
        
        try:
            for i in range(0, len(chat_history) - 1, 2):
                if i + 1 < len(chat_history):
                    user_msg = chat_history[i]
                    ai_response = chat_history[i + 1]
                    
                    if user_msg.get('role') == 'user' and ai_response.get('role') == 'assistant':
                        # Create training example
                        training_example = {
                            "instruction": user_msg.get('content', ''),
                            "input": "",
                            "output": ai_response.get('content', '')
                        }
                        
                        # Add disease context if available
                        if disease_name:
                            training_example["input"] = f"Context: {disease_name} epidemic monitoring"
                        
                        training_data.append(training_example)
            
            return training_data
            
        except Exception as e:
            logger.error(f"Error generating fine-tuning data: {e}")
            return []

    def save_fine_tuning_dataset(self, training_data, disease_name, source='chat_history'):
        """
        Save fine-tuning dataset to database.
        
        Args:
            training_data: List of training examples
            disease_name: Disease name
            source: Source of the data
        """
        try:
            from chat.models import FineTuningDataset
            
            for example in training_data:
                FineTuningDataset.objects.create(
                    disease_name=disease_name,
                    instruction=example['instruction'],
                    input_text=example.get('input', ''),
                    output_text=example['output'],
                    source=source,
                    is_approved=True
                )
            
            logger.info(f"Saved {len(training_data)} fine-tuning examples for {disease_name}")
            
        except Exception as e:
            logger.error(f"Error saving fine-tuning dataset: {e}")

    def export_fine_tuning_data(self, disease_name=None, format='json'):

        """
        Export fine-tuning data for Vertex AI.
        
        Args:
            disease_name: Optional disease filter
            format: Export format ('json' or 'csv')
            
        Returns:
            str: Path to exported file
        """
        from django.utils import timezone
        try:
            from chat.models import FineTuningDataset
            import json
            import csv
            import os
            from django.conf import settings
            
            # Query approved fine-tuning data
            queryset = FineTuningDataset.objects.filter(is_approved=True)
            if disease_name:
                queryset = queryset.filter(disease_name__iexact=disease_name)
            
            # Convert to training format
            training_data = []
            for item in queryset:
                training_data.append(item.to_training_format())
            
            # Create export directory
            export_dir = os.path.join(settings.BASE_DIR, 'exports', 'fine_tuning')
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            disease_suffix = f"_{disease_name}" if disease_name else "_all"
            filename = f"fine_tuning_data{disease_suffix}_{timestamp}.{format}"
            filepath = os.path.join(export_dir, filename)
            
            # Export data
            if format == 'json':
                with open(filepath, 'w') as f:
                    json.dump(training_data, f, indent=2)
            elif format == 'csv':
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['instruction', 'input', 'output'])
                    writer.writeheader()
                    writer.writerows(training_data)
            
            logger.info(f"Exported fine-tuning data to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting fine-tuning data: {e}")
            return None

    def load_fine_tuned_model(self, disease_name):
        """
        Load fine-tuned Vertex AI model for specific disease.
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            bool: True if model loaded successfully
        """
        try:
            import vertexai
            from vertexai.preview.generative_models import GenerativeModel
            import json
            import os
            
            # Load endpoint information
            endpoint_file = f'model_endpoints/{disease_name}_endpoint.json'
            if not os.path.exists(endpoint_file):
                logger.warning(f"No fine-tuned model found for {disease_name}")
                return False
            
            with open(endpoint_file, 'r') as f:
                endpoint_info = json.load(f)
            
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            
            # Load the fine-tuned model
            model_name = endpoint_info['model_name']
            fine_tuned_model = GenerativeModel(model_name)
            
            # Store in symptom_models
            self.symptom_models[disease_name] = fine_tuned_model
            
            logger.info(f"Loaded fine-tuned model for {disease_name}: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading fine-tuned model for {disease_name}: {e}")
            return False

    def analyze_chat_message_with_fine_tuned(self, user_message, disease_name):
        """
        Analyze user chat message using fine-tuned model if available.
        
        Args:
            user_message (str): User's chat message
            disease_name (str): Disease name
            
        Returns:
            str: Response from fine-tuned model or fallback to base model
        """
        try:
            # Try to use fine-tuned model first
            if disease_name in self.symptom_models:
                fine_tuned_model = self.symptom_models[disease_name]
                
                # Create prompt for fine-tuned model
                prompt = f"""
                You are a specialized AI assistant for {disease_name} epidemic monitoring.
                
                User Question: {user_message}
                
                Please provide a helpful, accurate, and professional response about {disease_name}.
                """
                
                response = fine_tuned_model.generate_content(prompt)
                return response.text.strip()
            
            # Fallback to base model
            else:
                return self.analyze_chat_message(user_message)
                
        except Exception as e:
            logger.error(f"Error with fine-tuned model for {disease_name}: {e}")
            # Fallback to base model
            return self.analyze_chat_message(user_message)

    def get_available_fine_tuned_models(self):
        """
        Get list of available fine-tuned models.
        
        Returns:
            list: List of disease names with fine-tuned models
        """
        try:
            import os
            import json
            
            available_models = []
            model_dir = 'model_endpoints'
            
            if os.path.exists(model_dir):
                for file in os.listdir(model_dir):
                    if file.endswith('_endpoint.json'):
                        disease_name = file.replace('_endpoint.json', '')
                        available_models.append(disease_name)
            
            return available_models
            
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []

    def load_all_fine_tuned_models(self):
        """
        Load all available fine-tuned models.
        
        Returns:
            int: Number of models loaded
        """
        try:
            available_models = self.get_available_fine_tuned_models()
            loaded_count = 0
            
            for disease_name in available_models:
                if self.load_fine_tuned_model(disease_name):
                    loaded_count += 1
            
            logger.info(f"Loaded {loaded_count} fine-tuned models")
            return loaded_count
            
        except Exception as e:
            logger.error(f"Error loading fine-tuned models: {e}")
            return 0
