"""
Enhanced IBM Watsonx.ai Diagnostic Tool
Diagnoses configuration issues and provides actionable solutions
"""
import os
import sys
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials

# Load environment variables
load_dotenv()

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title):
    """Print a section header"""
    print(f"\n{'-' * 70}")
    print(f"  {title}")
    print(f"{'-' * 70}")

def print_success(message):
    """Print success message"""
    print(f"[+] {message}")

def print_error(message):
    """Print error message"""
    print(f"[X] {message}")

def print_warning(message):
    """Print warning message"""
    print(f"[!] {message}")

def print_info(message):
    """Print info message"""
    print(f"[*] {message}")

def test_api_key_validity(api_key, url):
    """Test if the API key is valid by making a simple API call"""
    print_section("Step 1: Testing API Key Validity")
    
    try:
        credentials = Credentials(api_key=api_key, url=url)
        client = APIClient(credentials)
        
        # Try to get account details
        print_info("Attempting to authenticate with IBM Cloud...")
        
        # Try a simple operation to verify authentication
        # Just creating the client is enough to test the API key
        _ = client.version
        
        print_success("API Key is VALID and authenticated successfully")
        return True, client
        
    except Exception as e:
        error_msg = str(e).lower()
        print_error(f"API Key authentication FAILED")
        print(f"\nError details: {str(e)}")
        
        if "401" in error_msg or "unauthorized" in error_msg:
            print_warning("The API key appears to be invalid or expired")
            print("\n[*] How to get a valid API key:")
            print("   1. Go to: https://cloud.ibm.com/iam/apikeys")
            print("   2. Click 'Create an IBM Cloud API key'")
            print("   3. Give it a name (e.g., 'watsonx-meeting-agent')")
            print("   4. Copy the API key immediately (you won't see it again)")
            print("   5. Update WATSONX_API_KEY in your .env file")
        
        return False, None

def test_project_access(client, project_id):
    """Test if the project ID is accessible"""
    print_section("Step 2: Testing Project ID and WML Association")
    
    try:
        print_info(f"Attempting to access project: {project_id}")
        
        # Try to set the project
        client.set.default_project(project_id)
        
        print_success("Project ID exists and is accessible")
        
        # Now test if it's associated with WML by trying to access models
        print_info("Verifying Watson Machine Learning association...")
        
        try:
            # This will fail with 403 if not associated with WML
            models = client.foundation_models.get_model_specs()
            print_success("Project IS properly associated with Watson Machine Learning")
            return True
        except Exception as wml_error:
            wml_error_msg = str(wml_error)
            if "403" in wml_error_msg and "not associated with a WML instance" in wml_error_msg:
                print_error("Project is NOT associated with Watson Machine Learning instance")
                print("\n" + "=" * 70)
                print("  PROBLEM IDENTIFIED: Missing WML Association")
                print("=" * 70)
                print("\nYour project exists and you have access to it, but it's not")
                print("associated with a Watson Machine Learning (WML) service instance.")
                print("\nThis is a common issue and easy to fix!")
                print("\n" + "=" * 70)
                print("  SOLUTION: Create a New Project with WML")
                print("=" * 70)
                print("\nThe easiest fix is to create a NEW project that's properly configured:")
                print("\n[STEP 1] Go to Watson Studio Projects")
                print("   URL: https://dataplatform.cloud.ibm.com/projects")
                print("\n[STEP 2] Click 'New project' button")
                print("\n[STEP 3] Select 'Create an empty project'")
                print("\n[STEP 4] Fill in project details:")
                print("   - Name: 'AI Meeting Rescue Agent' (or any name you prefer)")
                print("   - Description: Optional")
                print("\n[STEP 5] IMPORTANT - Associate with Watson Machine Learning:")
                print("   - Look for 'Select storage service' section")
                print("   - You should also see 'Associate a Watson Machine Learning service'")
                print("   - If you have a WML service, select it from the dropdown")
                print("   - If you DON'T have one, click 'Create a new service instance'")
                print("\n[STEP 6] After project creation:")
                print("   - Click on the project to open it")
                print("   - Go to 'Manage' tab (or Settings)")
                print("   - Click on 'General' section")
                print("   - Find and COPY the 'Project ID' (36-character UUID)")
                print("\n[STEP 7] Update your .env file:")
                print("   - Open the .env file in your project")
                print("   - Replace the WATSONX_PROJECT_ID value with your new Project ID")
                print("   - Save the file")
                print("\n[STEP 8] Run this diagnostic again:")
                print("   python diagnose_watsonx.py")
                print("\n" + "=" * 70)
                print("  ALTERNATIVE: Associate Existing Project with WML")
                print("=" * 70)
                print("\nIf you want to keep using your current project:")
                print("\n[OPTION A] Through Watson Studio:")
                print("   1. Go to: https://dataplatform.cloud.ibm.com/projects")
                print("   2. Open your project")
                print("   3. Go to 'Manage' tab -> 'Services & integrations'")
                print("   4. Click 'Associate service'")
                print("   5. Select 'Watson Machine Learning'")
                print("   6. Choose your WML instance or create a new one")
                print("\n[OPTION B] Create WML Service First (if you don't have one):")
                print("   1. Go to: https://cloud.ibm.com/catalog/services/watson-machine-learning")
                print("   2. Select a plan (Lite plan is free)")
                print("   3. Choose a region (must match your project region)")
                print("   4. Click 'Create'")
                print("   5. Then follow Option A above to associate it")
                print("\n" + "=" * 70)
                return False
            else:
                # Some other error
                raise wml_error
        
    except Exception as e:
        error_msg = str(e)
        
        # Skip if we already handled the WML association error above
        if "not associated with a WML instance" in error_msg:
            return False
            
        print_error(f"Project access FAILED")
        print(f"\nError details: {error_msg}")
        
        # Check for specific error codes
        if "403" in error_msg and "not associated" not in error_msg:
            print_error("HTTP 403 Forbidden - Access denied")
            print("\n[SOLUTION]")
            print("   You don't have permission to access this project.")
            print("   Make sure you're using the correct IBM Cloud account.")
            
        elif "404" in error_msg:
            print_error("HTTP 404 Not Found - Project ID does not exist")
            print("\n[SOLUTION]")
            print("   The project ID is incorrect or doesn't exist.")
            print("\n[*] How to find the correct Project ID:")
            print("   1. Go to: https://dataplatform.cloud.ibm.com/projects")
            print("   2. Click on your project")
            print("   3. Go to Settings → General")
            print("   4. Copy the 'Project ID' (36-character UUID)")
            print("   5. Update WATSONX_PROJECT_ID in your .env file")
            
        elif "401" in error_msg:
            print_error("HTTP 401 Unauthorized - No access to this project")
            print("\n[SOLUTION]")
            print("   You don't have permission to access this project.")
            print("   Make sure you're using the correct IBM Cloud account")
            print("   and that you have access to the project.")
        
        return False

def test_model_access(client, project_id, model_id):
    """Test if models can be accessed - this is now done in test_project_access"""
    print_section("Step 3: Verifying Model Configuration")
    
    try:
        print_info("Checking configured model...")
        
        # Get model specs (should work if we got here)
        models = client.foundation_models.get_model_specs()
        
        if models and 'resources' in models:
            model_count = len(models['resources'])
            print_success(f"Successfully retrieved {model_count} available models")
            
            # Check if the configured model is available
            available_model_ids = [m.get('model_id') for m in models['resources']]
            
            if model_id in available_model_ids:
                print_success(f"Configured model '{model_id}' is available")
            else:
                print_warning(f"Configured model '{model_id}' not found")
                print("\n[*] Available Granite models:")
                granite_models = [m for m in available_model_ids if 'granite' in m.lower()]
                for i, model in enumerate(granite_models[:10], 1):
                    print(f"   {i}. {model}")
                
                if granite_models:
                    print(f"\n[TIP] Consider using one of these models in your .env file")
            
            return True
        else:
            print_warning("No models found or unexpected response format")
            return False
            
    except Exception as e:
        # This shouldn't happen if test_project_access passed
        print_error(f"Model access test failed: {str(e)}")
        return False

def run_diagnostics():
    """Run complete diagnostic suite"""
    print_header("IBM Watsonx.ai Configuration Diagnostics")
    
    # Get configuration
    api_key = os.getenv('WATSONX_API_KEY')
    project_id = os.getenv('WATSONX_PROJECT_ID')
    url = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
    model_id = os.getenv('GRANITE_MODEL_ID', 'ibm/granite-13b-chat-v2')
    
    print_section("Current Configuration")
    print(f"   URL:        {url}")
    print(f"   API Key:    {'*' * 20}{api_key[-4:] if api_key and len(api_key) > 4 else 'NOT SET'}")
    print(f"   Project ID: {project_id if project_id else 'NOT SET'}")
    print(f"   Model ID:   {model_id}")
    
    # Check if credentials are set
    if not api_key or not project_id:
        print_error("\nMissing required credentials in .env file")
        print("\n[*] Required environment variables:")
        if not api_key:
            print("   [X] WATSONX_API_KEY is not set")
        if not project_id:
            print("   [X] WATSONX_PROJECT_ID is not set")
        
        print("\n[!] Please set these variables in your .env file")
        return False
    
    # Test API key
    api_valid, client = test_api_key_validity(api_key, url)
    if not api_valid:
        return False
    
    # Test project access
    project_valid = test_project_access(client, project_id)
    if not project_valid:
        return False
    
    # Test model access
    model_valid = test_model_access(client, project_id, model_id)
    
    # Final summary
    print_header("Diagnostic Summary")
    
    if api_valid and project_valid and model_valid:
        print_success("All tests PASSED!")
        print("\n[SUCCESS] Your configuration is correct and ready to use!")
        print("\nYou can now run your application with:")
        print("   python run.py")
        return True
    else:
        print_error("Some tests FAILED")
        print("\n[!] Please follow the instructions above to fix the issues")
        print("\n[*] Additional Resources:")
        print("   - IBM Cloud Console: https://cloud.ibm.com/")
        print("   - Watson Studio Projects: https://dataplatform.cloud.ibm.com/projects")
        print("   - API Keys: https://cloud.ibm.com/iam/apikeys")
        print("   - Watson Machine Learning: https://cloud.ibm.com/catalog/services/watson-machine-learning")
        return False

if __name__ == "__main__":
    try:
        success = run_diagnostics()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[X] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob
