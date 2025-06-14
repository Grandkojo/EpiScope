import pandas as pd
import logging
from src.models.disease_monitor import DiseaseMonitor
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load data
        logger.info("Loading data")
        diabetes_data = pd.read_csv('artifacts/csv/health_data_eams_diabetes.csv')
        malaria_data = pd.read_csv('artifacts/csv/health_data_eams_malaria.csv')
        
        # Initialize and train model
        logger.info("Initializing DiseaseMonitor")
        monitor = DiseaseMonitor()
        
        logger.info("Training models")
        monitor.train_model(diabetes_data, malaria_data)
        
        # Save models
        logger.info("Saving models")
        monitor.save_models()
        
        logger.info("Training completed successfully")
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    main() 