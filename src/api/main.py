from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from models.disease_monitor import DiseaseMonitor
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Disease Monitoring API",
    description="API for monitoring and predicting diabetes and malaria cases in Ghana",
    version="1.0.0"
)

# Initialize the model
monitor = DiseaseMonitor()
try:
    monitor.load_models()
    logger.info("Models loaded successfully")
except Exception as e:
    logger.error(f"Error loading models: {str(e)}")
    raise

class PatientData(BaseModel):
    age: float
    sex: str
    location: str
    nhia_patient: bool
    pregnant: bool = False

class PredictionResponse(BaseModel):
    disease_type: str
    prediction: bool
    probability: float
    risk_level: str

@app.post("/predict/{disease_type}", response_model=PredictionResponse)
async def predict_disease(disease_type: str, patient_data: PatientData):
    """
    Predict disease risk for a patient
    """
    try:
        if disease_type not in ['diabetes', 'malaria']:
            raise HTTPException(status_code=400, detail="Invalid disease type")
        
        # Convert patient data to DataFrame
        df = pd.DataFrame([{
            'Age': patient_data.age,
            'Sex': patient_data.sex,
            'Address (Locality)': patient_data.location,
            'NHIA Patient': 'Yes' if patient_data.nhia_patient else 'No',
            'Pregnant Patient': 'Yes' if patient_data.pregnant else 'No'
        }])
        
        # Make prediction
        predictions, probabilities = monitor.predict(df, disease_type)
        
        # Calculate risk level
        probability = probabilities[0][1]  # Probability of positive class
        risk_level = "High" if probability > 0.7 else "Medium" if probability > 0.3 else "Low"
        
        return PredictionResponse(
            disease_type=disease_type,
            prediction=bool(predictions[0]),
            probability=float(probability),
            risk_level=risk_level
        )
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 