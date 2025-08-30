#!/usr/bin/env python3
"""
Standalone script to generate SHAP plots for existing v2 models
Run this script to create comprehensive SHAP visualizations for your trained models
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function from the training script
from disease_monitor.data_preprocessing_v2 import generate_shap_for_existing_models

if __name__ == "__main__":
    print("🚀 SHAP Plot Generator for EpiScope v2 Models")
    print("=" * 60)
    
    # Check if required packages are installed
    try:
        import shap
        import matplotlib.pyplot as plt
        import pandas as pd
        import numpy as np
        import pickle
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install: pip install shap matplotlib pandas numpy")
        sys.exit(1)
    
    # Generate SHAP plots
    generate_shap_for_existing_models()
    
    print("\n🎉 SHAP plot generation completed!")
    print("Check the 'src/artifacts/shap_plots/' directory for the generated visualizations.") 