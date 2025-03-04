"""
Test script to verify Django configuration works outside of service context.
Run this script directly on the Windows server to diagnose issues.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    print("=" * 60)
    print("Django Configuration Test Script")
    print("=" * 60)

    # 1. Check paths and environment
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Add the project directory to Python path
    sys.path.insert(0, script_dir)
    
    # 2. Configure Django settings
    print("\nSetting up Django environment...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_requisition.settings')
    
    # 3. Try importing Django
    print("Importing Django...")
    try:
        import django
        print(f"Django version: {django.__version__}")
        
        print("Setting up Django...")
        django.setup()
        print("Django setup successful.")
        
        # 4. Try getting WSGI application
        print("\nTesting WSGI application...")
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        print("WSGI application created successfully.")
        
        # 5. Test database connection
        print("\nTesting database connection...")
        from django.db import connection
        connection.ensure_connection()
        print("Database connection successful.")
        
        # 6. Test importing project models
        print("\nTesting model imports...")
        from apps.orders.models import LabOrder
        print(f"Found LabOrder model: {LabOrder}")
        
        # 7. Test if waitress can serve the application
        print("\nTesting Waitress import...")
        from waitress import serve
        print("Waitress imported successfully.")
        
        print("\nAll tests PASSED! Your Django environment is working correctly.")
        print("If the Windows service is still failing, check permissions and service account settings.")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nTest FAILED. Fix the above errors before trying to run as a service.")

if __name__ == '__main__':
    main()