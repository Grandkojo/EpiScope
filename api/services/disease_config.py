"""
Disease configuration for analytics service
This file contains the configuration for all supported diseases including their filters, codes, and metadata.

To add a new disease, simply add a new entry to the DISEASE_CONFIG dictionary following this pattern:

'new_disease_name': {
    'name': 'Display Name',
    'description': 'Description of the disease',
    'filters': {
        'text_filters': ['text to search for'],
        'regex_patterns': [r'regex pattern for ICD codes'],
        'code_patterns': ['specific codes to match']
    },
    'icd_codes': ['ICD-10 codes'],
    'symptoms': ['Common symptoms list']
}

The system will automatically:
1. Load the disease from the database
2. Create file paths for CSV and time series data
3. Build database queries using the filters
4. Make all analytics methods work with the new disease
"""

from typing import Dict, List, Any

# Disease configuration dictionary
DISEASE_CONFIG = {
    'diabetes': {
        'name': 'Diabetes',
        'description': 'Diabetes is a chronic condition that affects the way your body uses and stores sugar.',
        'filters': {
            'text_filters': ['diabetes', 'diabetic'],
            'regex_patterns': [r'\bE0[89]|E1[013]\b', r'\bE11\b', r'\bE10\b'],
            'code_patterns': ['MEDI02A', 'MEDI03A', 'DIABETES']
        },
        'icd_codes': ['E08', 'E09', 'E10', 'E11', 'E13'],
        'symptoms': ['Frequent Urination', 'Excessive Thirst', 'Unexplained Weight Loss', 'Fatigue', 'Blurred Vision']
    },
    'malaria': {
        'name': 'Malaria',
        'description': 'Malaria is a life-threatening disease caused by parasites transmitted through mosquito bites.',
        'filters': {
            'text_filters': ['malaria', 'plasmodium'],
            'regex_patterns': [r'\bB5[0-4]\b', r'\bB50\b', r'\bB51\b', r'\bB52\b', r'\bB53\b', r'\bB54\b'],
            'code_patterns': ['MEDI28A', 'MALARIA']
        },
        'icd_codes': ['B50', 'B51', 'B52', 'B53', 'B54'],
        'symptoms': ['Fever', 'Headache', 'Chills and Shivering', 'Sweating', 'Nausea and Vomiting']
    },
    'cholera': {
        'name': 'Cholera',
        'description': 'Cholera is an acute diarrheal infection caused by ingestion of contaminated food or water.',
        'filters': {
            'text_filters': ['cholera', 'vibrio'],
            'regex_patterns': [r'\bA0[0-9]\b', r'\bA00\b', r'\bA01\b'],
            'code_patterns': ['MEDI01A', 'CHOLERA']
        },
        'icd_codes': ['A00', 'A01'],
        'symptoms': ['Severe Diarrhea', 'Vomiting', 'Dehydration', 'Leg Cramps', 'Rapid Heart Rate']
    },
    'meningitis': {
        'name': 'Meningitis',
        'description': 'Meningitis is an inflammation of the protective membranes covering the brain and spinal cord.',
        'filters': {
            'text_filters': ['meningitis', 'meningococcal'],
            'regex_patterns': [r'\bG0[0-9]\b', r'\bA39\b', r'\bG00\b', r'\bG01\b', r'\bG02\b', r'\bG03\b'],
            'code_patterns': ['MEDI04A', 'MENINGITIS']
        },
        'icd_codes': ['A39', 'G00', 'G01', 'G02', 'G03'],
        'symptoms': ['Severe Headache', 'Stiff Neck', 'Fever', 'Nausea', 'Sensitivity to Light']
    },
    'tuberculosis': {
        'name': 'Tuberculosis',
        'description': 'Tuberculosis is a bacterial infection that primarily affects the lungs.',
        'filters': {
            'text_filters': ['tuberculosis', 'tb', 'mycobacterium'],
            'regex_patterns': [r'\bA1[5-9]\b', r'\bB90\b', r'\bA15\b', r'\bA16\b', r'\bA17\b', r'\bA18\b', r'\bA19\b'],
            'code_patterns': ['MEDI05A', 'TUBERCULOSIS']
        },
        'icd_codes': ['A15', 'A16', 'A17', 'A18', 'A19', 'B90'],
        'symptoms': ['Persistent Cough', 'Chest Pain', 'Coughing Up Blood', 'Fatigue', 'Night Sweats']
    },
    'hiv_aids': {
        'name': 'HIV/AIDS',
        'description': 'HIV is a virus that attacks the immune system, leading to AIDS if untreated.',
        'filters': {
            'text_filters': ['hiv', 'aids', 'human immunodeficiency virus'],
            'regex_patterns': [r'\bB2[0-4]\b', r'\bZ21\b', r'\bB20\b', r'\bB21\b', r'\bB22\b', r'\bB23\b', r'\bB24\b'],
            'code_patterns': ['MEDI06A', 'HIV', 'AIDS']
        },
        'icd_codes': ['B20', 'B21', 'B22', 'B23', 'B24', 'Z21'],
        'symptoms': ['Fever', 'Fatigue', 'Swollen Lymph Nodes', 'Weight Loss', 'Recurrent Infections']
    },
    'hypertension': {
        'name': 'Hypertension',
        'description': 'Hypertension is high blood pressure that can lead to serious health complications.',
        'filters': {
            'text_filters': ['hypertension', 'high blood pressure', 'htn'],
            'regex_patterns': [r'\bI1[0-5]\b', r'\bI10\b', r'\bI11\b', r'\bI12\b', r'\bI13\b', r'\bI14\b', r'\bI15\b'],
            'code_patterns': ['MEDI07A', 'HYPERTENSION']
        },
        'icd_codes': ['I10', 'I11', 'I12', 'I13', 'I14', 'I15'],
        'symptoms': ['Headache', 'Shortness of Breath', 'Nosebleeds', 'Chest Pain', 'Dizziness']
    },
    'asthma': {
        'name': 'Asthma',
        'description': 'Asthma is a chronic respiratory condition that causes airway inflammation and narrowing.',
        'filters': {
            'text_filters': ['asthma', 'bronchial asthma'],
            'regex_patterns': [r'\bJ4[5-6]\b', r'\bJ45\b', r'\bJ46\b'],
            'code_patterns': ['MEDI08A', 'ASTHMA']
        },
        'icd_codes': ['J45', 'J46'],
        'symptoms': ['Wheezing', 'Shortness of Breath', 'Chest Tightness', 'Coughing', 'Difficulty Breathing']
    }
}

def get_disease_config(disease_name: str = None) -> Dict[str, Any]:
    """
    Get disease configuration
    
    Args:
        disease_name: Name of the disease (lowercase). If None, returns all configurations.
    
    Returns:
        Dictionary containing disease configuration(s)
    """
    if disease_name:
        return DISEASE_CONFIG.get(disease_name.lower(), {})
    return DISEASE_CONFIG

def get_available_diseases() -> List[str]:
    """
    Get list of all available disease names
    
    Returns:
        List of disease names
    """
    return list(DISEASE_CONFIG.keys())

def get_disease_filters(disease_name: str) -> Dict[str, Any]:
    """
    Get filters for a specific disease
    
    Args:
        disease_name: Name of the disease (lowercase)
    
    Returns:
        Dictionary containing filter configuration
    """
    config = get_disease_config(disease_name)
    return config.get('filters', {
        'text_filters': [disease_name],
        'regex_patterns': [],
        'code_patterns': []
    })

def get_disease_icd_codes(disease_name: str) -> List[str]:
    """
    Get ICD codes for a specific disease
    
    Args:
        disease_name: Name of the disease (lowercase)
    
    Returns:
        List of ICD codes
    """
    config = get_disease_config(disease_name)
    return config.get('icd_codes', [])

def get_disease_symptoms(disease_name: str) -> List[str]:
    """
    Get common symptoms for a specific disease
    
    Args:
        disease_name: Name of the disease (lowercase)
    
    Returns:
        List of common symptoms
    """
    config = get_disease_config(disease_name)
    return config.get('symptoms', [])

def is_disease_supported(disease_name: str) -> bool:
    """
    Check if a disease is supported
    
    Args:
        disease_name: Name of the disease (lowercase)
    
    Returns:
        True if disease is supported, False otherwise
    """
    return disease_name.lower() in DISEASE_CONFIG 