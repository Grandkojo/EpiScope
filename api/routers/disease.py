from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from src.models.disease_monitor import DiseaseMonitor

router = APIRouter(
    prefix="/disease",
    tags=["disease"],
    responses={404: {"description": "Not found"}},
)

class PredictionRequest(BaseModel):
    age: str
    sex: str
    nhia_patient: str
    pregnant: str
    location: str

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    disease_type: str

@router.post("/predict/{disease_type}", response_model=PredictionResponse)
async def predict_disease(disease_type: str, request: PredictionRequest):
    """
    Make predictions for a given disease type (diabetes or malaria)
    """
    try:
        # Create a DataFrame from the request
        data = pd.DataFrame([{
            'Age': request.age,
            'Sex': request.sex,
            'NHIA Patient': request.nhia_patient,
            'Pregnant Patient': request.pregnant,
            'Address (Locality)': request.location
        }])
        
        # Initialize the model
        monitor = DiseaseMonitor()
        monitor.load_models()
        
        # Make prediction
        predictions, probabilities = monitor.predict(data, disease_type)
        
        return PredictionResponse(
            prediction=int(predictions[0]),
            probability=float(probabilities[0][1]),
            disease_type=disease_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"} 