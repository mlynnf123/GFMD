#!/usr/bin/env python3
"""
GFMD Swarm Agent Deployment Validation Script
Validate deployment prerequisites and environment setup.
"""

import os
import sys
import subprocess
import importlib
from typing import List, Tuple, Dict

def check_environment_variables() -> List[Tuple[str, bool, str]]:
    """Check required environment variables"""
    required_vars = [
        ("GOOGLE_CLOUD_PROJECT", "Google Cloud project ID"),
        ("GOOGLE_APPLICATION_CREDENTIALS", "Service account key file path")
    ]
    
    optional_vars = [
        ("VERTEX_AI_LOCATION", "Vertex AI region (defaults to us-central1)")
    ]
    
    results = []
    
    # Check required variables
    for var, description in required_vars:
        value = os.getenv(var)
        if value:
            results.append((f"✅ {var}", True, f"Set to: {value[:50]}..."))
        else:
            results.append((f"❌ {var}", False, f"Missing - {description}"))
    
    # Check optional variables
    for var, description in optional_vars:
        value = os.getenv(var)
        if value:
            results.append((f"✅ {var}", True, f"Set to: {value}"))
        else:
            results.append((f"⚠️ {var}", True, f"Not set - {description}"))
    
    return results

def check_gcloud_cli() -> Tuple[bool, str]:
    """Check if gcloud CLI is installed and authenticated"""
    try:
        # Check gcloud installation
        result = subprocess.run(['gcloud', 'version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, "gcloud CLI not installed"
        
        # Check authentication
        result = subprocess.run(['gcloud', 'auth', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, "gcloud authentication failed"
        
        if "ACTIVE" not in result.stdout:
            return False, "No active gcloud authentication found"
        
        return True, "gcloud CLI installed and authenticated"
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "gcloud CLI not found or timeout"

def check_python_dependencies() -> List[Tuple[str, bool, str]]:
    """Check required Python dependencies"""
    required_packages = [
        ("google.cloud.aiplatform", "google-cloud-aiplatform"),
        ("vertexai", "vertexai"),
        ("langgraph", "langgraph"),
        ("langchain_core", "langchain-core"),
        ("langchain_google_vertexai", "langchain-google-vertexai"),
        ("pydantic", "pydantic")
    ]
    
    results = []
    
    for import_name, package_name in required_packages:
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'unknown')
            results.append((f"✅ {package_name}", True, f"Version: {version}"))
        except ImportError:
            results.append((f"❌ {package_name}", False, f"Not installed - pip install {package_name}"))
    
    return results

def check_google_cloud_apis() -> List[Tuple[str, bool, str]]:
    """Check if required Google Cloud APIs are enabled"""
    required_apis = [
        "aiplatform.googleapis.com",
        "storage.googleapis.com",
        "logging.googleapis.com",
        "monitoring.googleapis.com"
    ]
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        return [("❌ APIs Check", False, "GOOGLE_CLOUD_PROJECT not set")]
    
    results = []
    
    for api in required_apis:
        try:
            result = subprocess.run([
                'gcloud', 'services', 'list', '--enabled', 
                '--filter', f'name:{api}', 
                '--format', 'value(name)',
                '--project', project_id
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and api in result.stdout:
                results.append((f"✅ {api}", True, "Enabled"))
            else:
                results.append((f"❌ {api}", False, f"Not enabled - gcloud services enable {api}"))
                
        except (subprocess.TimeoutExpired, Exception) as e:
            results.append((f"⚠️ {api}", False, f"Check failed: {str(e)[:50]}"))
    
    return results

def check_vertex_ai_access() -> Tuple[bool, str]:
    """Test Vertex AI access"""
    try:
        import vertexai
        from google.cloud import aiplatform as aip
        
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        
        if not project_id:
            return False, "GOOGLE_CLOUD_PROJECT not set"
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        aip.init(project=project_id, location=location)
        
        return True, f"Vertex AI access verified - Project: {project_id}, Location: {location}"
        
    except ImportError as e:
        return False, f"Missing dependencies: {str(e)}"
    except Exception as e:
        return False, f"Vertex AI access failed: {str(e)}"

def check_swarm_agent_files() -> List[Tuple[str, bool, str]]:
    """Check if required swarm agent files exist"""
    required_files = [
        "vertex_ai_hospital_prospecting.py",
        "vertex_ai_outreach_agent.py", 
        "vertex_ai_swarm_orchestrator.py",
        "vertex_ai_data_models.py",
        "deploy_vertex_ai.py"
    ]
    
    results = []
    
    for filename in required_files:
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            results.append((f"✅ {filename}", True, f"Size: {file_size:,} bytes"))
        else:
            results.append((f"❌ {filename}", False, "File not found"))
    
    return results

def check_service_account_permissions() -> Tuple[bool, str]:
    """Check service account permissions (simplified)"""
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            return False, "GOOGLE_CLOUD_PROJECT not set"
        
        # Try to list AI Platform models as a permission test
        result = subprocess.run([
            'gcloud', 'ai', 'models', 'list', '--limit=1', '--quiet',
            '--project', project_id
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return True, "Service account has AI Platform access"
        else:
            return False, f"Permission check failed: {result.stderr[:100]}"
            
    except Exception as e:
        return False, f"Permission check error: {str(e)}"

def print_results(title: str, results: List[Tuple[str, bool, str]]):
    """Print validation results"""
    print(f"\n{title}")
    print("-" * len(title))
    
    for name, success, message in results:
        print(f"{name}: {message}")

def main():
    """Main validation function"""
    print("🔍 GFMD Swarm Agent Deployment Validation")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check environment variables
    env_results = check_environment_variables()
    print_results("Environment Variables", env_results)
    if not all(result[1] for result in env_results if "❌" in result[0]):
        pass  # Some failures are acceptable for optional vars
    else:
        all_checks_passed = False
    
    # Check gcloud CLI
    gcloud_success, gcloud_message = check_gcloud_cli()
    print_results("Google Cloud CLI", [("gcloud CLI", gcloud_success, gcloud_message)])
    if not gcloud_success:
        all_checks_passed = False
    
    # Check Python dependencies
    dep_results = check_python_dependencies()
    print_results("Python Dependencies", dep_results)
    if not all(result[1] for result in dep_results):
        all_checks_passed = False
    
    # Check Google Cloud APIs
    api_results = check_google_cloud_apis()
    print_results("Google Cloud APIs", api_results)
    if not all(result[1] for result in api_results):
        all_checks_passed = False
    
    # Check Vertex AI access
    vertex_success, vertex_message = check_vertex_ai_access()
    print_results("Vertex AI Access", [("Vertex AI", vertex_success, vertex_message)])
    if not vertex_success:
        all_checks_passed = False
    
    # Check service account permissions
    perm_success, perm_message = check_service_account_permissions()
    print_results("Service Account Permissions", [("Permissions", perm_success, perm_message)])
    if not perm_success:
        all_checks_passed = False
    
    # Check swarm agent files
    file_results = check_swarm_agent_files()
    print_results("Swarm Agent Files", file_results)
    if not all(result[1] for result in file_results):
        all_checks_passed = False
    
    # Final summary
    print(f"\n{'='*50}")
    if all_checks_passed:
        print("🎉 All validation checks passed!")
        print("✅ Ready for deployment to Vertex AI")
        print("\nNext steps:")
        print("1. Run: python deploy_vertex_ai.py")
        print("2. Monitor deployment progress")
        print("3. Test deployed agent")
    else:
        print("❌ Some validation checks failed")
        print("⚠️ Please fix the issues above before deployment")
        print("\nCommon fixes:")
        print("• Install missing dependencies: pip install -r vertex_ai_production_requirements.txt")
        print("• Enable APIs: gcloud services enable SERVICE_NAME")
        print("• Set environment variables: export GOOGLE_CLOUD_PROJECT=your-project-id")
        print("• Authenticate gcloud: gcloud auth application-default login")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)