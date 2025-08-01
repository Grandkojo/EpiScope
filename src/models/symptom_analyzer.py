import pandas as pd
import numpy as np
import json
import logging
from typing import List, Dict, Tuple, Optional
from disease_monitor.models import CommonSymptom, Disease

# Import Vertex AI
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

logger = logging.getLogger(__name__)

class SymptomAnalyzer:
    """
    Specialized class for symptom analysis using Vertex AI models.
    Can be used for both zero-shot analysis and fine-tuned models.
    """
    
    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-1.5-pro"):
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.client = None
        self.fine_tuned_models = {}
        
        if VERTEX_AI_AVAILABLE:
            self._initialize_client()
        else:
            logger.error("Vertex AI not available. Please install google-cloud-aiplatform")
            raise ImportError("Vertex AI not available")
    
    def _initialize_client(self):
        """Initialize Vertex AI client."""
        try:
            vertexai.init(project=self.project_id, location=self.location)
            self.client = GenerativeModel(self.model_name)
            logger.info(f"Vertex AI client initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI client: {e}")
            raise
    
    def create_symptom_training_data(self, disease_name: str, symptoms_list: List[str]) -> List[Dict]:
        """
        Create training data for fine-tuning symptom analysis models.
        
        Args:
            disease_name: Name of the disease
            symptoms_list: List of symptom descriptions
            
        Returns:
            List of training examples with symptoms and expected scores
        """
        try:
            disease_obj = Disease.objects.get(disease_name__iexact=disease_name)
            expected_symptoms = list(CommonSymptom.objects.filter(disease=disease_obj)
                                   .values_list('symptom', flat=True))
            
            training_data = []
            
            for symptoms in symptoms_list:
                # Calculate similarity score based on symptom overlap
                symptom_words = set(symptoms.lower().split())
                expected_words = set()
                for exp_symptom in expected_symptoms:
                    expected_words.update(exp_symptom.lower().split())
                
                # Calculate Jaccard similarity
                intersection = len(symptom_words.intersection(expected_words))
                union = len(symptom_words.union(expected_words))
                similarity = intersection / union if union > 0 else 0
                
                # Add some noise and context-based adjustments
                base_score = similarity * 0.8 + 0.1  # Base score between 0.1 and 0.9
                
                # Add training example
                training_data.append({
                    "symptoms": symptoms,
                    "disease": disease_name,
                    "expected_symptoms": expected_symptoms,
                    "score": base_score,
                    "explanation": f"Score based on {similarity:.2f} similarity with expected symptoms"
                })
            
            return training_data
            
        except Disease.DoesNotExist:
            logger.error(f"Disease '{disease_name}' not found in database")
            return []
    
    def analyze_symptoms_zero_shot(self, symptoms_text: str, disease_name: str) -> Dict:
        """
        Analyze symptoms using zero-shot Vertex AI approach.
        
        Args:
            symptoms_text: Patient symptoms description
            disease_name: Disease to analyze for
            
        Returns:
            Dictionary with score, confidence, and explanation
        """
        try:
            disease_obj = Disease.objects.get(disease_name__iexact=disease_name)
            expected_symptoms = list(CommonSymptom.objects.filter(disease=disease_obj)
                                   .order_by('rank')
                                   .values_list('symptom', flat=True))
            
            prompt = f"""
            You are a medical symptom analyzer. Analyze the following symptoms for {disease_name} risk assessment.
            
            PATIENT SYMPTOMS: {symptoms_text}
            
            EXPECTED SYMPTOMS FOR {disease_name.upper()}: {', '.join(expected_symptoms)}
            
            Please provide a JSON response with the following structure:
            {{
                "risk_score": <float between 0.0 and 1.0>,
                "confidence": <float between 0.0 and 1.0>,
                "key_matches": [<list of matching symptoms>],
                "missing_symptoms": [<list of expected symptoms not present>],
                "explanation": "<brief explanation of the assessment>"
            }}
            
            Guidelines:
            - 0.0-0.3: Low risk (few or no matching symptoms)
            - 0.3-0.6: Moderate risk (some symptoms match)
            - 0.6-0.8: High risk (many symptoms match)
            - 0.8-1.0: Very high risk (strong symptom pattern match)
            
            Consider symptom severity, frequency, and combination patterns.
            """
            
            response = self.client.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    # Validate and clamp scores
                    result['risk_score'] = max(0.0, min(1.0, float(result.get('risk_score', 0.5))))
                    result['confidence'] = max(0.0, min(1.0, float(result.get('confidence', 0.5))))
                    
                    return result
                else:
                    raise ValueError("No JSON found in response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                # Fallback: extract score using regex
                import re
                score_match = re.search(r'0\.\d+|\d+\.\d+', response_text)
                fallback_score = float(score_match.group()) if score_match else 0.5
                
                return {
                    "risk_score": max(0.0, min(1.0, fallback_score)),
                    "confidence": 0.3,
                    "key_matches": [],
                    "missing_symptoms": expected_symptoms,
                    "explanation": "Fallback analysis due to parsing error"
                }
                
        except Exception as e:
            logger.error(f"Error in symptom analysis: {e}")
            return {
                "risk_score": 0.5,
                "confidence": 0.0,
                "key_matches": [],
                "missing_symptoms": [],
                "explanation": f"Analysis failed: {str(e)}"
            }
    
    def batch_analyze_symptoms(self, symptoms_list: List[str], disease_name: str) -> List[Dict]:
        """
        Analyze multiple symptom descriptions in batch.
        
        Args:
            symptoms_list: List of symptom descriptions
            disease_name: Disease to analyze for
            
        Returns:
            List of analysis results
        """
        results = []
        for symptoms in symptoms_list:
            result = self.analyze_symptoms_zero_shot(symptoms, disease_name)
            result['input_symptoms'] = symptoms
            results.append(result)
        
        return results
    
    def create_fine_tuning_dataset(self, disease_name: str, 
                                 positive_examples: List[str],
                                 negative_examples: List[str]) -> List[Dict]:
        """
        Create a dataset for fine-tuning Gemini models on specific diseases.
        
        Args:
            disease_name: Disease to create dataset for
            positive_examples: List of symptom descriptions that indicate the disease
            negative_examples: List of symptom descriptions that don't indicate the disease
            
        Returns:
            List of training examples
        """
        training_data = []
        
        # Add positive examples
        for symptoms in positive_examples:
            training_data.append({
                "input": f"Symptoms: {symptoms}\nDisease: {disease_name}",
                "output": "High risk - symptoms strongly indicate this disease",
                "score": 0.9
            })
        
        # Add negative examples
        for symptoms in negative_examples:
            training_data.append({
                "input": f"Symptoms: {symptoms}\nDisease: {disease_name}",
                "output": "Low risk - symptoms don't indicate this disease",
                "score": 0.1
            })
        
        return training_data
    
    def get_symptom_insights(self, symptoms_text: str, disease_name: str) -> Dict:
        """
        Get detailed insights about symptoms in relation to a disease.
        
        Args:
            symptoms_text: Patient symptoms
            disease_name: Disease to analyze
            
        Returns:
            Dictionary with detailed insights
        """
        try:
            disease_obj = Disease.objects.get(disease_name__iexact=disease_name)
            expected_symptoms = list(CommonSymptom.objects.filter(disease=disease_obj)
                                   .order_by('rank')
                                   .values_list('symptom', flat=True))
            
            prompt = f"""
            Provide detailed medical insights about the following symptoms in relation to {disease_name}.
            
            PATIENT SYMPTOMS: {symptoms_text}
            
            EXPECTED SYMPTOMS FOR {disease_name.upper()}: {', '.join(expected_symptoms)}
            
            Please provide a comprehensive analysis including:
            1. Symptom severity assessment
            2. Risk level explanation
            3. Recommended next steps
            4. Differential diagnosis considerations
            5. Urgency indicators
            
            Format as JSON:
            {{
                "severity": "<low/moderate/high/critical>",
                "risk_level": "<low/moderate/high>",
                "urgency": "<low/medium/high/emergency>",
                "recommended_actions": [<list of actions>],
                "differential_diagnosis": [<other possible conditions>],
                "key_concerns": [<list of concerning symptoms>],
                "reassuring_factors": [<list of reassuring symptoms>]
            }}
            """
            
            response = self.client.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    return {"error": "Could not parse insights response"}
                    
            except json.JSONDecodeError:
                return {"error": "Invalid JSON in insights response"}
                
        except Exception as e:
            logger.error(f"Error getting symptom insights: {e}")
            return {"error": f"Analysis failed: {str(e)}"} 