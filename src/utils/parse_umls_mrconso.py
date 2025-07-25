import os
import pickle
from collections import defaultdict

MRCONSO_PATH = os.path.join(os.path.dirname(__file__), '../artifacts/umls/MRCONSO.RRF')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '../artifacts/umls/code_to_terms.pkl')

# UMLS source vocabularies of interest (ICD10, SNOMEDCT, MSH, etc.)
SOURCES = {'ICD10', 'ICD10CM', 'SNOMEDCT_US', 'MSH', 'ICD9', 'ICD9CM'}

# Only keep English terms
LANG = 'ENG'

# Map: code (e.g., ICD10 code) -> set of terms/synonyms
code_to_terms = defaultdict(set)

with open(MRCONSO_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    for i, line in enumerate(f):
        parts = line.strip().split('|')
        if len(parts) < 15:
            continue
        cui = parts[0]  # UMLS Concept Unique Identifier
        lang = parts[1]
        term_status = parts[2]  # P=preferred, S=synonym
        source = parts[11]      # e.g., ICD10, SNOMEDCT_US, MSH
        code = parts[13]        # e.g., E08.40
        term = parts[14]        # the actual term
        if lang == LANG and source in SOURCES and code:
            code_to_terms[code].add(term)
        if i % 1000000 == 0 and i > 0:
            print(f"Processed {i} lines...")

# Save mapping
with open(OUTPUT_PATH, 'wb') as f:
    pickle.dump(dict(code_to_terms), f)

print(f"Saved code-to-terms mapping with {len(code_to_terms)} codes to {OUTPUT_PATH}") 