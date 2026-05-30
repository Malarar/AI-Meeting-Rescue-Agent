"""
Test IBM Watsonx.ai Credentials
This script verifies if your API key and project ID are valid
"""
import os
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai import Credentials

# Load environment variables
load_dotenv()

def test_credentials():
    """Test IBM Watsonx.ai credentials"""
    
    print("=" * 60)
    print("IBM Watsonx.ai Credentials Test")
    print("=" * 60)
    
    # Get credentials from environment
    api_key = os.getenv('WATSONX_API_KEY')
    project_id = os.getenv('WATSONX_PROJECT_ID')
    url = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
    
    print(f"\n[*] Configuration:")
    print(f"   URL: {url}")
    print(f"   API Key: {'*' * 20}{api_key[-4:] if api_key and len(api_key) > 4 else 'NOT SET'}")
    print(f"   Project ID: {project_id if project_id else 'NOT SET'}")
    
    if not api_key or not project_id:
        print("\n[X] ERROR: Missing credentials in .env file")
        print("   Please set WATSONX_API_KEY and WATSONX_PROJECT_ID")
        return False
    
    print("\n[~] Testing connection...")
    
    try:
        # Create credentials object
        credentials = Credentials(
            api_key=api_key,
            url=url
        )
        
        # Initialize API client
        client = APIClient(credentials)
        
        print("[+] API client initialized successfully")
        
        # Test project access
        print(f"\n[~] Testing project access (ID: {project_id})...")
        client.set.default_project(project_id)
        
        print("[+] Project access verified")
        
        # Try to list available models
        print("\n[~] Fetching available foundation models...")
        
        from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes
        
        # Get model specs
        models = client.foundation_models.get_model_specs()
        
        if models:
            print(f"[+] Successfully retrieved {len(models.get('resources', []))} models")
            print("\n[*] Sample available models:")
            for i, model in enumerate(models.get('resources', [])[:5]):
                model_id = model.get('model_id', 'Unknown')
                print(f"   {i+1}. {model_id}")
        else:
            print("[!] No models found")
        
        print("\n" + "=" * 60)
        print("[+] ALL TESTS PASSED - Credentials are valid!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[X] ERROR: {str(e)}")
        print("\n" + "=" * 60)
        print("[X] CREDENTIAL TEST FAILED")
        print("=" * 60)
        
        print("\n[?] Troubleshooting:")
        print("   1. Verify your API key is correct and active")
        print("   2. Check that the project ID exists and you have access")
        print("   3. Ensure the project is associated with a Watson Machine Learning instance")
        print("   4. Verify the URL matches your IBM Cloud region")
        print("\n[i] Get credentials from: https://cloud.ibm.com/")
        
        return False

if __name__ == "__main__":
    test_credentials()

# Made with Bob
