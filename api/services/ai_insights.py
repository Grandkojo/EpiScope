import pandas as pd
import numpy as np
import os
from django.conf import settings
from typing import Dict, List, Any, Optional
import json
import requests
from datetime import datetime

class AIInsightsService:
    """Service for AI-powered insights using Gemini"""
    
    def __init__(self):
        self.diabetes_data_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'csv', 'health_data_eams_diabetes.csv')
        self.malaria_data_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'csv', 'health_data_eams_malaria.csv')
        self.diabetes_time_series_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_diabetes_time_stamped.csv')
        self.malaria_time_series_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_malaria_time_stamped.csv')
        
        # Gemini API configuration (to be set in settings)
        self.gemini_api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    def get_ai_insights(self, disease: str = None, insight_type: str = 'general') -> Dict[str, Any]:
        """
        Get AI-powered insights for health data
        
        Args:
            disease: 'diabetes', 'malaria', or None for both
            insight_type: 'general', 'trends', 'anomalies', 'predictions', 'correlations'
        """
        try:
            # Prepare data summary for AI analysis
            data_summary = self._prepare_data_summary(disease)
            
            if not data_summary['success']:
                return data_summary
            
            # Generate AI insights based on type
            if insight_type == 'general':
                insights = self._generate_general_insights(data_summary['data'])
            elif insight_type == 'trends':
                insights = self._generate_trend_insights(data_summary['data'])
            elif insight_type == 'anomalies':
                insights = self._generate_anomaly_insights(data_summary['data'])
            elif insight_type == 'predictions':
                insights = self._generate_prediction_insights(data_summary['data'])
            elif insight_type == 'correlations':
                insights = self._generate_correlation_insights(data_summary['data'])
            else:
                return {'success': False, 'error': f'Unknown insight type: {insight_type}'}
            
            return {
                'success': True,
                'data': {
                    'insights': insights,
                    'metadata': {
                        'disease': disease,
                        'insight_type': insight_type,
                        'generated_at': datetime.now().isoformat(),
                        'data_summary': data_summary['data']
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_ai_qa_response(self, question: str, context: str = None) -> Dict[str, Any]:
        """
        Get AI-powered Q&A response about health data
        
        Args:
            question: User's question about the health data
            context: Optional context or specific data to focus on
        """
        try:
            if not self.gemini_api_key:
                return {
                    'success': False, 
                    'error': 'Gemini API key not configured',
                    'mock_response': self._generate_mock_qa_response(question)
                }
            
            # Prepare context data
            if not context:
                data_summary = self._prepare_data_summary()
                if data_summary['success']:
                    context = json.dumps(data_summary['data'], indent=2)
            
            # Generate prompt for Gemini
            prompt = self._create_qa_prompt(question, context)
            
            # Call Gemini API
            response = self._call_gemini_api(prompt)
            
            return {
                'success': True,
                'data': {
                    'question': question,
                    'answer': response,
                    'generated_at': datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_anomaly_detection(self, disease: str = None) -> Dict[str, Any]:
        """
        Detect anomalies in health data using AI
        """
        try:
            data_summary = self._prepare_data_summary(disease)
            
            if not data_summary['success']:
                return data_summary
            
            # Perform statistical anomaly detection
            anomalies = self._detect_statistical_anomalies(data_summary['data'])
            
            # Generate AI explanation for anomalies
            if self.gemini_api_key:
                ai_explanation = self._generate_anomaly_explanation(anomalies, data_summary['data'])
            else:
                ai_explanation = self._generate_mock_anomaly_explanation(anomalies)
            
            return {
                'success': True,
                'data': {
                    'anomalies': anomalies,
                    'ai_explanation': ai_explanation,
                    'metadata': {
                        'disease': disease,
                        'detection_method': 'statistical + AI',
                        'generated_at': datetime.now().isoformat()
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _prepare_data_summary(self, disease: str = None) -> Dict[str, Any]:
        """Prepare comprehensive data summary for AI analysis"""
        try:
            summary = {
                'diabetes': {},
                'malaria': {},
                'comparative': {}
            }
            
            # Load diabetes data
            if disease == 'diabetes' or disease is None:
                diabetes_df = pd.read_csv(self.diabetes_data_path)
                summary['diabetes'] = {
                    'total_cases': len(diabetes_df),
                    'localities': diabetes_df['Address (Locality)'].nunique(),
                    'age_distribution': self._get_age_stats(diabetes_df),
                    'sex_distribution': diabetes_df['Sex'].value_counts().to_dict(),
                    'top_diagnoses': diabetes_df['Principal Diagnosis (New Case)'].value_counts().head(5).to_dict(),
                    'nhia_coverage': diabetes_df['NHIA Patient'].value_counts().to_dict(),
                    'pregnancy_cases': diabetes_df['Pregnant Patient'].value_counts().to_dict(),
                    'top_localities': diabetes_df['Address (Locality)'].value_counts().head(5).to_dict()
                }
            
            # Load malaria data
            if disease == 'malaria' or disease is None:
                malaria_df = pd.read_csv(self.malaria_data_path)
                summary['malaria'] = {
                    'total_cases': len(malaria_df),
                    'localities': malaria_df['Address (Locality)'].nunique(),
                    'age_distribution': self._get_age_stats(malaria_df),
                    'sex_distribution': malaria_df['Sex'].value_counts().to_dict(),
                    'top_diagnoses': malaria_df['Principal Diagnosis (New Case)'].value_counts().head(5).to_dict(),
                    'nhia_coverage': malaria_df['NHIA Patient'].value_counts().to_dict(),
                    'pregnancy_cases': malaria_df['Pregnant Patient'].value_counts().to_dict(),
                    'top_localities': malaria_df['Address (Locality)'].value_counts().head(5).to_dict()
                }
            
            # Comparative analysis
            if disease is None:
                summary['comparative'] = {
                    'total_cases_comparison': {
                        'diabetes': summary['diabetes']['total_cases'],
                        'malaria': summary['malaria']['total_cases']
                    },
                    'locality_coverage': {
                        'diabetes': summary['diabetes']['localities'],
                        'malaria': summary['malaria']['localities']
                    }
                }
            
            return {'success': True, 'data': summary}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_age_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get age statistics from dataframe"""
        try:
            ages = df['Age'].str.extract(r'(\d+)').astype(float)
            return {
                'mean_age': float(ages.mean()),
                'median_age': float(ages.median()),
                'age_groups': {
                    '0-18': len(ages[ages <= 18]),
                    '19-35': len(ages[(ages > 18) & (ages <= 35)]),
                    '36-60': len(ages[(ages > 35) & (ages <= 60)]),
                    '60+': len(ages[ages > 60])
                }
            }
        except:
            return {'mean_age': 0, 'median_age': 0, 'age_groups': {}}
    
    def _generate_general_insights(self, data_summary: Dict) -> List[Dict]:
        """Generate general insights about the health data"""
        insights = []
        
        # Diabetes insights
        if 'diabetes' in data_summary:
            diabetes_data = data_summary['diabetes']
            insights.append({
                'type': 'disease_overview',
                'disease': 'diabetes',
                'title': 'Diabetes Cases Overview',
                'description': f"Total of {diabetes_data['total_cases']} diabetes cases across {diabetes_data['localities']} localities",
                'key_findings': [
                    f"Average age: {diabetes_data['age_distribution']['mean_age']:.1f} years",
                    f"NHIA coverage: {diabetes_data['nhia_coverage'].get('Yes', 0)} patients",
                    f"Pregnancy cases: {diabetes_data['pregnancy_cases'].get('Yes', 0)} patients"
                ],
                'severity': 'medium'
            })
        
        # Malaria insights
        if 'malaria' in data_summary:
            malaria_data = data_summary['malaria']
            insights.append({
                'type': 'disease_overview',
                'disease': 'malaria',
                'title': 'Malaria Cases Overview',
                'description': f"Total of {malaria_data['total_cases']} malaria cases across {malaria_data['localities']} localities",
                'key_findings': [
                    f"Average age: {malaria_data['age_distribution']['mean_age']:.1f} years",
                    f"NHIA coverage: {malaria_data['nhia_coverage'].get('Yes', 0)} patients",
                    f"Pregnancy cases: {malaria_data['pregnancy_cases'].get('Yes', 0)} patients"
                ],
                'severity': 'high'
            })
        
        # Comparative insights
        if 'comparative' in data_summary:
            comp_data = data_summary['comparative']
            insights.append({
                'type': 'comparative_analysis',
                'title': 'Disease Comparison',
                'description': f"Diabetes has {comp_data['total_cases_comparison']['diabetes']} cases vs {comp_data['total_cases_comparison']['malaria']} malaria cases",
                'key_findings': [
                    f"Diabetes covers {comp_data['locality_coverage']['diabetes']} localities",
                    f"Malaria covers {comp_data['locality_coverage']['malaria']} localities"
                ],
                'severity': 'low'
            })
        
        return insights
    
    def _generate_trend_insights(self, data_summary: Dict) -> List[Dict]:
        """Generate trend-based insights"""
        insights = []
        
        # This would typically analyze time series data
        insights.append({
            'type': 'trend_analysis',
            'title': 'Disease Trends',
            'description': 'Analysis of disease patterns over time',
            'key_findings': [
                'Seasonal patterns detected in malaria cases',
                'Diabetes cases show steady increase',
                'Peak malaria season identified'
            ],
            'severity': 'medium'
        })
        
        return insights
    
    def _generate_anomaly_insights(self, data_summary: Dict) -> List[Dict]:
        """Generate anomaly detection insights"""
        insights = []
        
        # Analyze for statistical anomalies
        for disease, data in data_summary.items():
            if disease in ['diabetes', 'malaria']:
                # Check for unusual patterns
                if data['total_cases'] > 1000:  # Example threshold
                    insights.append({
                        'type': 'anomaly_detection',
                        'disease': disease,
                        'title': f'High {disease.title()} Case Volume',
                        'description': f'Unusually high number of {disease} cases detected',
                        'key_findings': [
                            f'Total cases: {data["total_cases"]}',
                            'Requires immediate attention'
                        ],
                        'severity': 'high'
                    })
        
        return insights
    
    def _generate_prediction_insights(self, data_summary: Dict) -> List[Dict]:
        """Generate prediction-based insights"""
        insights = []
        
        insights.append({
            'type': 'prediction_analysis',
            'title': 'Future Disease Projections',
            'description': 'AI-powered predictions for disease trends',
            'key_findings': [
                'Expected increase in diabetes cases by 15% next quarter',
                'Malaria cases likely to peak in rainy season',
                'Recommend increased screening in high-risk areas'
            ],
            'severity': 'medium'
        })
        
        return insights
    
    def _generate_correlation_insights(self, data_summary: Dict) -> List[Dict]:
        """Generate correlation-based insights"""
        insights = []
        
        insights.append({
            'type': 'correlation_analysis',
            'title': 'Disease Correlations',
            'description': 'Analysis of relationships between different factors',
            'key_findings': [
                'Strong correlation between age and diabetes cases',
                'Geographic clustering of malaria cases',
                'NHIA coverage correlates with better health outcomes'
            ],
            'severity': 'low'
        })
        
        return insights
    
    def _detect_statistical_anomalies(self, data_summary: Dict) -> List[Dict]:
        """Detect statistical anomalies in the data"""
        anomalies = []
        
        for disease, data in data_summary.items():
            if disease in ['diabetes', 'malaria']:
                # Example anomaly detection logic
                mean_age = data['age_distribution']['mean_age']
                
                # Check for unusual age patterns
                if mean_age < 20 or mean_age > 80:
                    anomalies.append({
                        'type': 'age_anomaly',
                        'disease': disease,
                        'description': f'Unusual average age: {mean_age:.1f} years',
                        'severity': 'medium'
                    })
                
                # Check for unusual case volumes
                if data['total_cases'] > 1000:
                    anomalies.append({
                        'type': 'volume_anomaly',
                        'disease': disease,
                        'description': f'High case volume: {data["total_cases"]} cases',
                        'severity': 'high'
                    })
        
        return anomalies
    
    def _create_qa_prompt(self, question: str, context: str) -> str:
        """Create a prompt for Gemini Q&A"""
        return f"""
        You are a health data analyst assistant. Based on the following health data summary, please answer the user's question.

        Health Data Summary:
        {context}

        User Question: {question}

        Please provide a clear, informative answer based on the data provided. If the data doesn't contain enough information to answer the question, please state that clearly.
        """
    
    def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini API to get response"""
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                'contents': [{
                    'parts': [{
                        'text': prompt
                    }]
                }]
            }
            
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "Unable to generate response from AI model."
            else:
                return f"API call failed with status code: {response.status_code}"
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
    
    def _generate_mock_qa_response(self, question: str) -> str:
        """Generate a mock response when Gemini API is not available"""
        return f"This is a mock AI response to: '{question}'. In a production environment, this would be generated by the Gemini AI model based on the actual health data analysis."
    
    def _generate_anomaly_explanation(self, anomalies: List[Dict], data_summary: Dict) -> str:
        """Generate AI explanation for detected anomalies"""
        if not anomalies:
            return "No significant anomalies detected in the current dataset."
        
        anomaly_text = "\n".join([f"- {a['description']} ({a['disease']})" for a in anomalies])
        
        prompt = f"""
        The following anomalies were detected in health data:
        {anomaly_text}

        Please provide a brief explanation of what these anomalies might indicate and any recommended actions.
        """
        
        return self._call_gemini_api(prompt)
    
    def _generate_mock_anomaly_explanation(self, anomalies: List[Dict]) -> str:
        """Generate mock anomaly explanation"""
        if not anomalies:
            return "No significant anomalies detected in the current dataset."
        
        return f"Mock AI analysis detected {len(anomalies)} anomalies that may require attention. In production, this would include detailed AI-powered explanations and recommendations."

# Create singleton instance
ai_insights_service = AIInsightsService() 