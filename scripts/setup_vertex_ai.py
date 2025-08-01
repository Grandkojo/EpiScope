#!/usr/bin/env python3
"""
Setup script for Vertex AI configuration for the Disease Monitor system.
This script helps users configure their Google Cloud project for Vertex AI usage.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_gcloud_installation():
    """Check if gcloud CLI is installed."""
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ gcloud CLI is installed")
            return True
        else:
            print("❌ gcloud CLI is not properly installed")
            return False
    except FileNotFoundError:
        print("❌ gcloud CLI is not installed")
        return False

def check_authentication():
    """Check if user is authenticated with gcloud."""
    try:
        result = subprocess.run(['gcloud', 'auth', 'list'], capture_output=True, text=True)
        if result.returncode == 0 and 'ACTIVE' in result.stdout:
            print("✅ gcloud authentication is active")
            return True
        else:
            print("❌ gcloud authentication is not active")
            return False
    except Exception as e:
        print(f"❌ Error checking authentication: {e}")
        return False

def list_projects():
    """List available Google Cloud projects."""
    try:
        result = subprocess.run(['gcloud', 'projects', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("\nAvailable projects:")
            print(result.stdout)
            return result.stdout
        else:
            print("❌ Error listing projects")
            return None
    except Exception as e:
        print(f"❌ Error listing projects: {e}")
        return None

def set_project(project_id):
    """Set the active Google Cloud project."""
    try:
        result = subprocess.run(['gcloud', 'config', 'set', 'project', project_id], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Project set to: {project_id}")
            return True
        else:
            print(f"❌ Error setting project: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting project: {e}")
        return False

def enable_apis(project_id):
    """Enable required APIs for Vertex AI."""
    apis = [
        'aiplatform.googleapis.com',  # Vertex AI API
        'compute.googleapis.com',     # Compute Engine API
        'storage.googleapis.com',     # Cloud Storage API
    ]
    
    for api in apis:
        try:
            print(f"Enabling {api}...")
            result = subprocess.run([
                'gcloud', 'services', 'enable', api, '--project', project_id
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {api} enabled")
            else:
                print(f"❌ Error enabling {api}: {result.stderr}")
        except Exception as e:
            print(f"❌ Error enabling {api}: {e}")

def create_service_account(project_id, service_account_name="disease-monitor-sa"):
    """Create a service account for the application."""
    try:
        # Create service account
        result = subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'create', service_account_name,
            '--display-name', 'Disease Monitor Service Account',
            '--project', project_id
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Service account created: {service_account_name}")
        else:
            if "already exists" in result.stderr:
                print(f"ℹ️ Service account already exists: {service_account_name}")
            else:
                print(f"❌ Error creating service account: {result.stderr}")
                return None
        
        # Grant necessary roles
        roles = [
            'roles/aiplatform.user',
            'roles/storage.objectViewer',
            'roles/storage.objectCreator'
        ]
        
        for role in roles:
            try:
                result = subprocess.run([
                    'gcloud', 'projects', 'add-iam-policy-binding', project_id,
                    '--member', f'serviceAccount:{service_account_name}@{project_id}.iam.gserviceaccount.com',
                    '--role', role
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Role {role} granted")
                else:
                    print(f"❌ Error granting role {role}: {result.stderr}")
            except Exception as e:
                print(f"❌ Error granting role {role}: {e}")
        
        return f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
        
    except Exception as e:
        print(f"❌ Error creating service account: {e}")
        return None

def create_service_account_key(project_id, service_account_email, key_file_path):
    """Create a service account key file."""
    try:
        result = subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'keys', 'create', key_file_path,
            '--iam-account', service_account_email,
            '--project', project_id
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Service account key created: {key_file_path}")
            return True
        else:
            print(f"❌ Error creating service account key: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating service account key: {e}")
        return False

def create_env_file(project_id, location, key_file_path):
    """Create a .env file with the necessary environment variables."""
    env_content = f"""# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT={project_id}
GOOGLE_CLOUD_LOCATION={location}
GOOGLE_APPLICATION_CREDENTIALS={key_file_path}

# Disease Monitor Configuration
DISEASE_MONITOR_LOG_LEVEL=INFO
DISEASE_MONITOR_MODEL_PATH=models/
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_vertex_ai_connection(project_id, location):
    """Test the Vertex AI connection."""
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        vertexai.init(project=project_id, location=location)
        model = GenerativeModel("gemini-1.5-pro")
        
        # Simple test
        response = model.generate_content("Hello, this is a test.")
        if response.text:
            print("✅ Vertex AI connection successful")
            return True
        else:
            print("❌ Vertex AI connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Vertex AI connection test failed: {e}")
        return False

def main():
    print("🚀 Vertex AI Setup for Disease Monitor")
    print("=" * 50)
    
    # Check prerequisites
    if not check_gcloud_installation():
        print("\nPlease install gcloud CLI first:")
        print("https://cloud.google.com/sdk/docs/install")
        return
    
    if not check_authentication():
        print("\nPlease authenticate with gcloud:")
        print("gcloud auth login")
        return
    
    # List projects
    projects_output = list_projects()
    if not projects_output:
        return
    
    # Get project ID
    project_id = input("\nEnter your Google Cloud project ID: ").strip()
    if not project_id:
        print("❌ Project ID is required")
        return
    
    # Set project
    if not set_project(project_id):
        return
    
    # Enable APIs
    print(f"\nEnabling APIs for project: {project_id}")
    enable_apis(project_id)
    
    # Create service account
    print(f"\nCreating service account...")
    service_account_email = create_service_account(project_id)
    if not service_account_email:
        return
    
    # Create service account key
    key_file_path = f"keys/{project_id}-service-account-key.json"
    os.makedirs("keys", exist_ok=True)
    
    if not create_service_account_key(project_id, service_account_email, key_file_path):
        return
    
    # Get location
    location = input("\nEnter your preferred location (default: us-central1): ").strip()
    if not location:
        location = "us-central1"
    
    # Create .env file
    print(f"\nCreating environment configuration...")
    if not create_env_file(project_id, location, key_file_path):
        return
    
    # Test connection
    print(f"\nTesting Vertex AI connection...")
    if test_vertex_ai_connection(project_id, location):
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the example: python examples/disease_prediction_example.py")
        print("3. Check the documentation: docs/DISEASE_MONITOR_ARCHITECTURE.md")
    else:
        print("\n⚠️ Setup completed but Vertex AI connection test failed.")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main() 