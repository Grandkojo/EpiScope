import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from vertexai.generative_models import GenerativeModel
import vertexai
from episcope.settings import GCP_PROJECT_ID, GCP_LOCATION

# Initialize Vertex AI
vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)

# Load Gemini model
model = GenerativeModel("gemini-2.0-flash-001")

# Construct prompt
prompt = """
You are a health data analyst. Provide a brief summary (max 3-4 sentences) comparing these diabetes trends:

2024: 199,336 cases, 812 deaths
2025: 34,608 cases, 87 deaths
"""

# Call model
response = model.generate_content(prompt)

print(response.text)
