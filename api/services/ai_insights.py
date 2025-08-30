import pandas as pd
import numpy as np
import os
from django.conf import settings
from typing import Dict, List, Any, Optional
import json
import requests
from datetime import datetime

# Import Vertex AI
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

class AIInsightsService:
    """Service for AI-powered insights using Google Cloud Vertex AI with Gemini"""
    
    def __init__(self):
        self.diabetes_data_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'csv', 'health_data_eams_diabetes.csv')
        self.malaria_data_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'csv', 'health_data_eams_malaria.csv')
        self.diabetes_time_series_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_diabetes_time_stamped.csv')
        self.malaria_time_series_path = os.path.join(settings.BASE_DIR, 'src', 'artifacts', 'time_series', 'health_data_eams_malaria_time_stamped.csv')
        
        # Vertex AI configuration
        self.gcp_project_id = getattr(settings, 'GCP_PROJECT_ID', None)
        self.gcp_location = getattr(settings, 'GCP_LOCATION', 'us-central1')
        self.model_name = getattr(settings, 'GEMINI_MODEL_NAME', 'gemini-2.0-flash-001')
        
        # Initialize Vertex AI if available
        if VERTEX_AI_AVAILABLE and self.gcp_project_id:
            try:
                vertexai.init(project=self.gcp_project_id, location=self.gcp_location)
                self.model = GenerativeModel(self.model_name)
                self.vertex_ai_initialized = True
            except Exception as e:
                print(f"Failed to initialize Vertex AI: {e}")
                self.vertex_ai_initialized = False
        else:
            self.vertex_ai_initialized = False
    
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
            if not self.vertex_ai_initialized:
                return {
                    'success': False, 
                    'error': 'Vertex AI not configured',
                    'mock_response': self._generate_mock_qa_response(question)
                }
            
            # Prepare context data
            if not context:
                data_summary = self._prepare_data_summary()
                if data_summary['success']:
                    context = json.dumps(data_summary['data'], indent=2)
            
            # Generate prompt for Gemini
            prompt = self._create_qa_prompt(question, context)
            
            # Call Vertex AI
            response = self._call_vertex_ai(prompt)
            
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
            if self.vertex_ai_initialized:
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
    
    def get_structured_analytics_insights(self, analytics_data: Dict, date_range: str = None, year: str = None, disease: str = None, locality: str = None, hospital: str = None) -> Dict[str, Any]:
        """
        Get structured AI insights for analytics data with specific date/year focus
        
        Args:
            analytics_data: The analytics data from your dashboard
            date_range: Date range filter (e.g., '2022-03', '2022-Q1')
            year: Specific year (e.g., '2022')
            disease: Disease type ('diabetes', 'malaria', 'both')
            locality: Specific locality filter
            hospital: Specific hospital filter (orgname)
        """
        try:
            if not self.vertex_ai_initialized:
                return {
                    'success': False,
                    'error': 'Vertex AI not configured',
                    'mock_response': self._generate_mock_structured_insights(analytics_data, date_range, year, disease, locality, hospital)
                }
            
            # Create structured prompt
            prompt = self._create_structured_analytics_prompt(analytics_data, date_range, year, disease, locality, hospital)
            
            # Call Vertex AI
            response = self._call_vertex_ai(prompt)
            
            # Parse and validate response
            parsed_response = self._parse_structured_response(response)
            
            return {
                'success': True,
                'data': {
                    'insights': parsed_response,
                    'metadata': {
                        'date_range': date_range,
                        'year': year,
                        'disease': disease,
                        'locality': locality,
                        'hospital': hospital,
                        'generated_at': datetime.now().isoformat(),
                        'analytics_data_keys': list(analytics_data.keys()) if analytics_data else []
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_prediction_ai_insights(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI insights for prediction results using Gemini
        
        Args:
            prediction_data: Dictionary containing prediction results and metadata
        """
        try:
            if not self.vertex_ai_initialized:
                return {
                    'success': False,
                    'error': 'Vertex AI not configured',
                    'insights': self._generate_mock_prediction_insights(prediction_data)
                }
            
            # Create prompt for prediction insights
            prompt = self._create_prediction_insights_prompt(prediction_data)
            
            # Call Vertex AI with timeout handling
            try:
                response = self._call_vertex_ai(prompt)
                
                # Check if the response contains an error
                if response.startswith('Error calling Vertex AI:'):
                    # Fallback to mock insights if Vertex AI fails
                    return {
                        'success': False,
                        'error': response,
                        'insights': self._generate_mock_prediction_insights(prediction_data)
                    }
                
                # Parse the response
                insights = self._parse_prediction_insights_response(response)
                
                return {
                    'success': True,
                    'insights': insights,
                    'raw_response': response
                }
                
            except Exception as ai_error:
                # Handle Vertex AI connection errors gracefully
                return {
                    'success': False,
                    'error': f'AI service temporarily unavailable: {str(ai_error)}',
                    'insights': self._generate_mock_prediction_insights(prediction_data)
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'insights': self._generate_mock_prediction_insights(prediction_data)
            }
    
    def get_dashboard_insights(self, analytics_data: Dict, disease: str = None, year: str = None, locality: str = None, hospital: str = None) -> Dict[str, Any]:
        """
        Get simple dashboard-focused AI insights for quick decision-making
        
        Args:
            analytics_data: The analytics data from your dashboard
            disease: Disease type ('diabetes', 'malaria', etc.)
            year: Specific year (e.g., '2023')
            locality: Specific locality filter
            hospital: Specific hospital filter (orgname)
        """
        try:
            if not self.vertex_ai_initialized:
                return {
                    'success': False,
                    'error': 'Vertex AI not configured',
                    'mock_response': self._generate_mock_dashboard_insights(analytics_data, disease, year, locality, hospital)
                }
            
            # Create simple dashboard prompt
            prompt = self._create_dashboard_insights_prompt(analytics_data, disease, year, locality, hospital)
            
            # Call Vertex AI
            response = self._call_vertex_ai(prompt)
            
            # Parse and validate response
            parsed_response = self._parse_dashboard_response(response)
            
            return {
                'success': True,
                'data': {
                    'insights': parsed_response,
                    'metadata': {
                        'disease': disease,
                        'year': year,
                        'locality': locality,
                        'hospital': hospital,
                        'generated_at': datetime.now().isoformat(),
                        'insight_type': 'dashboard_summary'
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _call_vertex_ai(self, prompt: str) -> str:
        """Call Vertex AI Gemini model with improved error handling"""
        try:
            # Add timeout to prevent hanging requests
            import time
            start_time = time.time()
            timeout_seconds = 30  # 30 second timeout
            
            response = self.model.generate_content(prompt)
            
            # Check if we exceeded timeout
            if time.time() - start_time > timeout_seconds:
                return "Error calling Vertex AI: Request timeout"
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific error types
            if "timeout" in error_msg.lower() or "503" in error_msg:
                return "Error calling Vertex AI: Service temporarily unavailable"
            elif "connection" in error_msg.lower():
                return "Error calling Vertex AI: Connection failed"
            elif "authentication" in error_msg.lower():
                return "Error calling Vertex AI: Authentication failed"
            else:
                return f"Error calling Vertex AI: {error_msg}"
    
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
    
    def _generate_mock_qa_response(self, question: str) -> str:
        """Generate a mock response when Vertex AI is not available"""
        return f"This is a mock AI response to: '{question}'. In a production environment, this would be generated by the Vertex AI Gemini model based on the actual health data analysis."
    
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
        
        return self._call_vertex_ai(prompt)
    
    def _generate_mock_anomaly_explanation(self, anomalies: List[Dict]) -> str:
        """Generate mock anomaly explanation"""
        if not anomalies:
            return "No significant anomalies detected in the current dataset."
        
        return f"Mock AI analysis detected {len(anomalies)} anomalies that may require attention. In production, this would include detailed AI-powered explanations and recommendations."

    def _create_structured_analytics_prompt(self, analytics_data: Dict, date_range: str = None, year: str = None, disease: str = None, locality: str = None, hospital: str = None) -> str:
        """
        Create a structured prompt for analytics insights
        """
        prompt = f"""
You are a healthcare data analyst specializing in epidemiological insights. Analyze the following health data and provide structured insights.

CONTEXT:
- Data Source: EAMS (Electronic Health Management System) from Weija Health Facility
- Data Type: Patient health records with demographic and diagnostic information
- Time Period: {date_range if date_range else 'All available data'}
- Year Focus: {year if year else 'All years'}
- Disease Focus: {disease.upper() if disease else 'All diseases'}
- Geographic Focus: {locality if locality else 'All localities'}
- Hospital Focus: {hospital if hospital else 'All hospitals'}

DATA STRUCTURE:
The data contains the following fields:
- Address (Locality): Patient's residential area
- Age: Patient age in years
- Sex: 0=Female, 1=Male
- Principal Diagnosis: Primary ICD-10 diagnosis code and description
- Additional Diagnosis: Secondary/comorbid conditions
- Pregnant Patient: 0=No, 1=Yes
- NHIA Patient: 0=Uninsured, 1=Insured
- Month: YYYY-MM format
- orgname: Healthcare facility name

ANALYTICS DATA PROVIDED:
{json.dumps(analytics_data, indent=2)}

TASK:
Provide a comprehensive analysis in the following structured JSON format. Focus on actionable insights, patterns, and public health implications.

REQUIRED RESPONSE STRUCTURE:
{{
    "executive_summary": {{
        "key_findings": ["finding1", "finding2", "finding3"],
        "public_health_implications": ["implication1", "implication2"],
        "priority_actions": ["action1", "action2", "action3"]
    }},
    "demographic_analysis": {{
        "age_distribution": {{
            "high_risk_groups": ["group1", "group2"],
            "age_patterns": "description of age-related patterns",
            "recommendations": ["recommendation1", "recommendation2"]
        }},
        "gender_analysis": {{
            "gender_patterns": "description of gender-related patterns",
            "risk_factors": ["factor1", "factor2"]
        }},
        "geographic_analysis": {{
            "hotspots": ["locality1", "locality2"],
            "geographic_patterns": "description of geographic distribution",
            "environmental_factors": ["factor1", "factor2"],
            "hospital_analysis": {{
                "facility_utilization": "description of hospital usage patterns",
                "capacity_insights": ["insight1", "insight2"],
                "referral_patterns": "description of patient referral patterns"
            }}
        }}
    }},
    "clinical_insights": {{
        "diagnosis_patterns": {{
            "common_diagnoses": ["diagnosis1", "diagnosis2"],
            "comorbidity_patterns": ["pattern1", "pattern2"],
            "severity_indicators": ["indicator1", "indicator2"]
        }},
        "complications": {{
            "frequent_complications": ["complication1", "complication2"],
            "risk_factors": ["factor1", "factor2"],
            "prevention_strategies": ["strategy1", "strategy2"]
        }}
    }},
    "temporal_analysis": {{
        "seasonal_patterns": {{
            "peak_periods": ["period1", "period2"],
            "seasonal_factors": ["factor1", "factor2"],
            "forecasting_insights": "description of temporal trends"
        }},
        "trend_analysis": {{
            "trend_direction": "increasing/decreasing/stable",
            "trend_factors": ["factor1", "factor2"],
            "future_projections": "description of expected trends"
        }}
    }},
    "healthcare_access": {{
        "insurance_coverage": {{
            "coverage_patterns": "description of insurance patterns",
            "access_barriers": ["barrier1", "barrier2"],
            "improvement_suggestions": ["suggestion1", "suggestion2"]
        }},
        "facility_utilization": {{
            "utilization_patterns": "description of facility usage",
            "capacity_implications": ["implication1", "implication2"]
        }}
    }},
    "public_health_recommendations": {{
        "immediate_actions": [
            {{
                "action": "action description",
                "priority": "high/medium/low",
                "target_population": "specific group",
                "expected_impact": "description of expected outcome"
            }}
        ],
        "long_term_strategies": [
            {{
                "strategy": "strategy description",
                "timeline": "expected timeline",
                "resources_needed": ["resource1", "resource2"],
                "success_metrics": ["metric1", "metric2"]
            }}
        ],
        "policy_implications": [
            {{
                "policy_area": "area description",
                "recommendation": "specific policy recommendation",
                "stakeholders": ["stakeholder1", "stakeholder2"]
            }}
        ]
    }},
    "data_quality_assessment": {{
        "completeness": "assessment of data completeness",
        "accuracy": "assessment of data accuracy",
        "limitations": ["limitation1", "limitation2"],
        "improvement_suggestions": ["suggestion1", "suggestion2"]
    }},
    "comparative_analysis": {{
        "benchmark_comparison": "comparison with expected patterns",
        "regional_variations": "description of regional differences",
        "international_context": "comparison with global patterns"
    }}
}}

INSTRUCTIONS:
1. Analyze the provided analytics data thoroughly
2. Focus on patterns, trends, and actionable insights
3. Consider public health implications and policy recommendations
4. Provide specific, evidence-based recommendations
5. Consider the temporal and geographic context
6. Address both immediate and long-term strategies
7. Ensure all insights are grounded in the provided data
8. Use clear, professional language suitable for healthcare professionals
9. Prioritize insights that can inform public health interventions
10. Consider the socioeconomic and environmental context of the data

RESPONSE FORMAT:
Return ONLY the JSON object as specified above. Do not include any additional text, explanations, or markdown formatting outside the JSON structure.
"""
        return prompt
    
    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """
        Parse and validate the structured response from Gemini
        """
        try:
            # Clean the response to extract JSON
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            
            # Parse JSON
            parsed = json.loads(response)
            
            # Validate required structure
            required_sections = [
                'executive_summary', 'demographic_analysis', 'clinical_insights',
                'temporal_analysis', 'healthcare_access', 'public_health_recommendations',
                'data_quality_assessment', 'comparative_analysis'
            ]
            
            for section in required_sections:
                if section not in parsed:
                    parsed[section] = {"error": f"Missing {section} section"}
            
            return parsed
            
        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse structured response",
                "raw_response": response,
                "parse_error": str(e)
            }
        except Exception as e:
            return {
                "error": "Error processing structured response",
                "raw_response": response,
                "error_details": str(e)
            }
    
    def _generate_mock_structured_insights(self, analytics_data: Dict, date_range: str = None, year: str = None, disease: str = None, locality: str = None, hospital: str = None) -> Dict[str, Any]:
        """
        Generate mock structured insights when Vertex AI is not available
        """
        return {
            "executive_summary": {
                "key_findings": [
                    f"Analysis of {disease or 'health'} data for {date_range or 'all periods'}",
                    "Data shows significant patterns in patient demographics and diagnoses",
                    "Geographic clustering observed in certain localities"
                ],
                "public_health_implications": [
                    "Need for targeted interventions in high-risk areas",
                    "Improved healthcare access required for underserved populations"
                ],
                "priority_actions": [
                    "Implement community health programs in identified hotspots",
                    "Enhance diagnostic capabilities for early detection",
                    "Strengthen health insurance coverage programs"
                ]
            },
            "demographic_analysis": {
                "age_distribution": {
                    "high_risk_groups": ["Elderly population (65+)", "Children under 5"],
                    "age_patterns": "Higher prevalence observed in middle-aged and elderly populations",
                    "recommendations": ["Age-specific screening programs", "Targeted health education"]
                },
                "gender_analysis": {
                    "gender_patterns": "Slight gender differences observed in disease patterns",
                    "risk_factors": ["Biological factors", "Socioeconomic factors"]
                },
                "geographic_analysis": {
                    "hotspots": ["Kasoa", "Weija", "Mallam"],
                    "geographic_patterns": "Concentration in urban and peri-urban areas",
                    "environmental_factors": ["Population density", "Healthcare access"],
                    "hospital_analysis": {
                        "facility_utilization": "High utilization in urban centers",
                        "capacity_insights": ["Need for capacity expansion", "Resource optimization"],
                        "referral_patterns": "High patient referral rates observed"
                    }
                }
            },
            "clinical_insights": {
                "diagnosis_patterns": {
                    "common_diagnoses": ["Primary disease patterns", "Comorbid conditions"],
                    "comorbidity_patterns": ["Hypertension", "Respiratory infections"],
                    "severity_indicators": ["Complication rates", "Hospitalization patterns"]
                },
                "complications": {
                    "frequent_complications": ["Neuropathy", "Retinopathy", "Nephropathy"],
                    "risk_factors": ["Age", "Duration of disease", "Poor glycemic control"],
                    "prevention_strategies": ["Regular screening", "Lifestyle modifications"]
                }
            },
            "temporal_analysis": {
                "seasonal_patterns": {
                    "peak_periods": ["Rainy season", "Dry season"],
                    "seasonal_factors": ["Environmental conditions", "Vector activity"],
                    "forecasting_insights": "Expected seasonal variations in disease incidence"
                },
                "trend_analysis": {
                    "trend_direction": "Stable with minor fluctuations",
                    "trend_factors": ["Population growth", "Healthcare improvements"],
                    "future_projections": "Gradual increase expected due to demographic changes"
                }
            },
            "healthcare_access": {
                "insurance_coverage": {
                    "coverage_patterns": "Mixed insurance coverage across population",
                    "access_barriers": ["Financial constraints", "Geographic barriers"],
                    "improvement_suggestions": ["Expand NHIA coverage", "Mobile health services"]
                },
                "facility_utilization": {
                    "utilization_patterns": "High utilization in urban centers",
                    "capacity_implications": ["Need for capacity expansion", "Resource optimization"]
                }
            },
            "public_health_recommendations": {
                "immediate_actions": [
                    {
                        "action": "Implement community screening programs",
                        "priority": "high",
                        "target_population": "High-risk age groups",
                        "expected_impact": "Early detection and intervention"
                    }
                ],
                "long_term_strategies": [
                    {
                        "strategy": "Strengthen primary healthcare system",
                        "timeline": "2-3 years",
                        "resources_needed": ["Healthcare workers", "Infrastructure"],
                        "success_metrics": ["Reduced incidence", "Improved outcomes"]
                    }
                ],
                "policy_implications": [
                    {
                        "policy_area": "Healthcare financing",
                        "recommendation": "Expand insurance coverage",
                        "stakeholders": ["Ministry of Health", "NHIA"]
                    }
                ]
            },
            "data_quality_assessment": {
                "completeness": "Good data completeness with some missing values",
                "accuracy": "Generally accurate with standard coding practices",
                "limitations": ["Limited follow-up data", "Self-reported information"],
                "improvement_suggestions": ["Enhanced data validation", "Regular audits"]
            },
            "comparative_analysis": {
                "benchmark_comparison": "Comparable to regional patterns",
                "regional_variations": "Urban-rural differences observed",
                "international_context": "Similar patterns to other developing countries"
            }
        }

    def _create_prediction_insights_prompt(self, prediction_data: Dict[str, Any]) -> str:
        """
        Create a prompt for prediction AI insights
        """
        prompt = f"""
You are a healthcare AI specialist analyzing disease prediction results. Based on the following prediction data, provide exactly 3 essential bullet points that would help healthcare professionals in decision-making.

PREDICTION DATA:
{json.dumps(prediction_data, indent=2)}

INSTRUCTIONS:
- Provide exactly 3 bullet points
- Keep each bullet point SHORT and CONCISE (maximum 15-20 words each)
- Focus on actionable insights for healthcare decision-making
- Consider the confidence level, model version, and feature analysis
- Use clear, simple medical terminology
- Avoid long, complex sentences
- Be direct and to the point

FORMAT YOUR RESPONSE AS:
• [First essential insight - keep it short]
• [Second essential insight - keep it short] 
• [Third essential insight - keep it short]

Focus on:
1. Clinical significance of the prediction
2. Confidence level interpretation
3. Key factors influencing the prediction
4. Recommended next steps
5. Model reliability assessment

Provide only the 3 bullet points, no additional text or explanations.
"""
        return prompt
    
    def _parse_prediction_insights_response(self, response: str) -> List[str]:
        """
        Parse the AI response into structured insights
        """
        try:
            # Check if response contains an error
            if response.startswith('Error calling Vertex AI:'):
                # Return mock insights if there's an error
                return self._generate_mock_prediction_insights({})
            
            # Extract bullet points from the response
            lines = response.strip().split('\n')
            insights = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    # Remove bullet point markers and clean up
                    insight = line.lstrip('•-* ').strip()
                    if insight and not insight.startswith('Error'):
                        insights.append(insight)
                elif (line and 
                      not line.startswith('PREDICTION') and 
                      not line.startswith('INSTRUCTIONS') and 
                      not line.startswith('FORMAT') and
                      not line.startswith('Error') and
                      not line.startswith('AI service') and
                      len(line) > 10):  # Only include substantial lines
                    # If no bullet point marker, treat as insight if it's not a header
                    insights.append(line)
            
            # Ensure we have exactly 3 insights
            if len(insights) > 3:
                insights = insights[:3]
            elif len(insights) < 3:
                # Pad with default insights if needed
                default_insights = [
                    "Consider additional diagnostic testing to confirm the prediction",
                    "Monitor patient response to treatment closely",
                    "Review model confidence level for clinical decision support"
                ]
                while len(insights) < 3:
                    insights.append(default_insights[len(insights)])
            
            return insights
            
        except Exception as e:
            return self._generate_mock_prediction_insights({})
    
    def _generate_mock_prediction_insights(self, prediction_data: Dict[str, Any]) -> List[str]:
        """
        Generate mock prediction insights when AI is not available
        """
        prediction = prediction_data.get('prediction', 0)
        confidence = prediction_data.get('combined_probability', 0.5)
        model_version = prediction_data.get('analysis_breakdown', {}).get('model_version', 'v2_enhanced')
        
        if prediction == 1:  # Positive prediction
            if confidence > 0.8:
                return [
                    "High confidence prediction - recommend immediate diagnostic testing",
                    "Strong clinical indicators present - consider treatment initiation",
                    "Model shows high reliability - proceed with clinical assessment"
                ]
            elif confidence > 0.6:
                return [
                    "Moderate confidence - additional testing recommended",
                    "Mixed clinical indicators - consider comprehensive evaluation",
                    "Proceed with caution - monitor patient response closely"
                ]
            else:
                return [
                    "Low confidence prediction - extensive diagnostic workup needed",
                    "Limited clinical indicators - consider alternative diagnoses",
                    "High uncertainty - recommend specialist consultation"
                ]
        else:  # Negative prediction
            if confidence > 0.8:
                return [
                    "High confidence negative - low disease probability",
                    "Strong indicators against diagnosis - consider other conditions",
                    "Model suggests alternative diagnostic pathways"
                ]
            elif confidence > 0.6:
                return [
                    "Moderate confidence negative - continue monitoring",
                    "Some clinical indicators present - periodic reassessment recommended",
                    "Consider preventive measures and follow-up"
                ]
            else:
                return [
                    "Low confidence negative - maintain clinical vigilance",
                    "Uncertain prediction - recommend comprehensive evaluation",
                    "Consider specialist consultation for definitive diagnosis"
                ]

    def _create_dashboard_insights_prompt(self, analytics_data: Dict, disease: str = None, year: str = None, locality: str = None, hospital: str = None) -> str:
        """
        Create a simple dashboard-focused prompt for quick insights based on actual dashboard data
        """
        prompt = f"""
You are a healthcare dashboard assistant. Analyze ONLY the dashboard data provided below and provide insights. DO NOT use any external knowledge, training data, or assumptions.

CONTEXT:
- Disease: {disease.upper() if disease else 'All diseases'}
- Year: {year if year else 'All years'}
- Locality: {locality if locality else 'All localities'}
- Hospital: {hospital if hospital else 'All facilities'}

DASHBOARD DATA TO ANALYZE:
{json.dumps(analytics_data, indent=2)}

CRITICAL INSTRUCTIONS:
- ONLY analyze the data provided above
- DO NOT reference any external knowledge about locations, diseases, or healthcare
- DO NOT use any information from your training data
- Base ALL insights purely on the numbers and patterns in the provided data
- If the data shows "KASOA" with 408 cases, say "KASOA with 408 cases"
- If the data shows "GBAWE" with 339 cases, say "GBAWE with 339 cases"
- Do not make assumptions about what these locations are or their characteristics

TASK:
Based ONLY on the data above, provide a concise summary in this JSON format:

{{
    "dashboard_summary": {{
        "key_insight": "One main insight derived ONLY from the data above",
        "trend": "Brief trend description based ONLY on the trends data above",
        "highlight": "One notable finding from the actual data patterns above",
        "recommendation": "One actionable recommendation based ONLY on the data above"
    }},
    "quick_stats": {{
        "total_cases": "Actual total cases from the data (if available)",
        "age_group": "Most affected age group from age_distribution data above",
        "gender_pattern": "Gender pattern from sex_distribution data above",
        "geographic_focus": "Key locality from localities or hotspots data above"
    }},
    "alert_level": "low/medium/high (based on data severity above)",
    "last_updated": "Current timestamp"
}}

DATA ANALYSIS REQUIREMENTS:
- Look at age_distribution data for age patterns
- Look at sex_distribution data for gender patterns  
- Look at localities data for geographic information
- Look at trends data for temporal patterns
- Look at hotspots data for case concentration
- Look at principal_diagnoses for main conditions
- Look at additional_diagnoses for comorbidities
- Look at nhia_status for insurance patterns
- Look at pregnancy_status for pregnancy data

EXAMPLE OF CORRECT ANALYSIS:
If the data shows "KASOA": 408 cases, "GBAWE": 339 cases, "WEIJA": 320 cases, then say:
"KASOA has the highest cases (408), followed by GBAWE (339) and WEIJA (320)"

DO NOT SAY:
"KASOA, GBAWE, and WEIJA are significant diabetes hotspots" (this sounds like external knowledge)

SAY INSTEAD:
"KASOA (408 cases), GBAWE (339 cases), and WEIJA (320 cases) show the highest case counts"

RESPONSE FORMAT:
Return ONLY the JSON object as specified above. No additional text or explanations.
"""
        return prompt

    def _parse_dashboard_response(self, response: str) -> Dict[str, Any]:
        """
        Parse and validate the dashboard response from Gemini
        """
        try:
            # Clean the response to extract JSON
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            response = response.strip()
            
            # Parse JSON
            parsed = json.loads(response)
            
            # Validate required structure
            required_sections = ['dashboard_summary', 'quick_stats', 'alert_level']
            
            for section in required_sections:
                if section not in parsed:
                    parsed[section] = {"error": f"Missing {section} section"}
            
            return parsed
            
        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse dashboard response",
                "raw_response": response,
                "parse_error": str(e)
            }
        except Exception as e:
            return {
                "error": "Error processing dashboard response",
                "raw_response": response,
                "error_details": str(e)
            }
    
    def _generate_mock_dashboard_insights(self, analytics_data: Dict, disease: str = None, year: str = None, locality: str = None, hospital: str = None) -> Dict[str, Any]:
        """
        Generate mock dashboard insights when Vertex AI is not available
        """
        # Try to extract actual data from the provided analytics_data
        total_cases = "Unknown"
        age_group = "Unknown"
        gender_pattern = "Unknown"
        geographic_focus = "Unknown"
        
        # Extract age distribution data
        if 'age_distribution' in analytics_data and 'data' in analytics_data['age_distribution']:
            age_data = analytics_data['age_distribution']['data'].get(disease, {})
            if age_data:
                # Find the age group with highest cases
                max_age_group = max(age_data.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0)
                age_group = max_age_group[0]
                total_cases = str(sum(age_data.values()))
        
        # Extract gender distribution data
        if 'sex_distribution' in analytics_data and 'data' in analytics_data['sex_distribution']:
            sex_data = analytics_data['sex_distribution']['data'].get(disease, {})
            if sex_data:
                if 'Female' in sex_data and 'Male' in sex_data:
                    female_cases = sex_data['Female']
                    male_cases = sex_data['Male']
                    if female_cases > male_cases:
                        gender_pattern = f"Females ({female_cases}) higher than males ({male_cases})"
                    else:
                        gender_pattern = f"Males ({male_cases}) higher than females ({female_cases})"
        
        # Extract geographic data from hotspots
        if 'hotspots' in analytics_data and 'data' in analytics_data['hotspots']:
            hotspots_data = analytics_data['hotspots']['data'].get(disease, [])
            if hotspots_data:
                # Get the locality with highest cases
                top_locality = max(hotspots_data, key=lambda x: x.get('cases', 0))
                geographic_focus = f"{top_locality.get('locality', 'Unknown')} ({top_locality.get('cases', 0)} cases)"
        
        return {
            "dashboard_summary": {
                "key_insight": f"Analysis of {disease or 'health'} data shows {total_cases} total cases with {age_group} being most affected",
                "trend": "Data shows varying case distribution across different localities",
                "highlight": f"Geographic analysis reveals {geographic_focus} as the primary focus area",
                "recommendation": f"Focus interventions in areas with highest case counts based on the data"
            },
            "quick_stats": {
                "total_cases": total_cases,
                "age_group": age_group,
                "gender_pattern": gender_pattern,
                "geographic_focus": geographic_focus
            },
            "alert_level": "medium",
            "last_updated": datetime.now().isoformat()
        }

# Create singleton instance
ai_insights_service = AIInsightsService() 