"""
Run the Django app directly using Waitress without the Windows service wrapper.
This helps diagnose if issues are related to the service specifically or the Django app.
"""
import os
import sys

def main():
    print("Starting Django with Waitress directly (without Windows service)...")
    
    # Get the directory where this script is located
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Add project directory to Python path
    sys.path.insert(0, base_dir)
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_requisition.settings')
    
    try:
        # Import Django and set it up
        import django
        django.setup()
        
        # Get the WSGI application
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        
        # Print server info
        print(f"Django version: {django.__version__}")
        print("Starting Waitress server on http://0.0.0.0:8000")
        print("Press Ctrl+C to exit")
        
        # Start Waitress
        from waitress import serve
        serve(application, host='0.0.0.0', port=8000, threads=4)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == '__main__':
    sys.exit(main())