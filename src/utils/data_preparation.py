import pandas as pd
from disease_monitor.models import CommonSymptom, Disease
import re


def extract_symptoms_from_text(text, disease_type=None):
    """
    Extract symptoms from diagnosis text using the CommonSymptom model.
    If disease_type is provided, only use symptoms associated with that disease.
    """
    if not isinstance(text, str):
        return []
    text = text.lower()
    if disease_type:
        try:
            disease_obj = Disease.objects.get(disease_name__iexact=disease_type)
            symptom_qs = CommonSymptom.objects.filter(disease=disease_obj)
            symptoms = list(symptom_qs.values_list('symptom', flat=True))
        except Exception:
            symptoms = []
    else:
        symptoms = list(CommonSymptom.objects.all().values_list('symptom', flat=True))
    found = []
    for symptom in symptoms:
        # Use word boundaries to avoid partial matches
        if re.search(r'\b' + re.escape(symptom.lower()) + r'\b', text):
            found.append(symptom)
    return found


def combine_and_label_datasets(df_pos, df_neg, target_col, disease_type, neg_label=0, pos_label=1):
    """
    Combine two dataframes (positives and negatives), assign target labels, and backfill symptoms if missing.
    - df_pos: DataFrame with positive cases (target disease)
    - df_neg: DataFrame with negative cases (other disease)
    - target_col: Name of the target column to create
    - disease_type: Name of the disease for positive class
    - neg_label: Label for negatives (default 0)
    - pos_label: Label for positives (default 1)
    Returns: Combined DataFrame with target labels and symptoms injected
    """
    df_pos = df_pos.copy()
    df_neg = df_neg.copy()
    df_pos[target_col] = pos_label
    df_neg[target_col] = neg_label
    combined = pd.concat([df_pos, df_neg], ignore_index=True)
    # Backfill symptoms if missing
    if 'symptoms' not in combined.columns:
        combined['symptoms'] = None
    for idx, row in combined.iterrows():
        if not isinstance(row.get('symptoms', None), list) or not row['symptoms']:
            diag_text = str(row.get('principal_diagnosis', '')) + ' ' + str(row.get('additional_diagnosis', ''))
            combined.at[idx, 'symptoms'] = extract_symptoms_from_text(diag_text, disease_type)
    return combined 