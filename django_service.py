import os
import sys
import time
import win32service
import win32serviceutil
import win32event
import servicemanager
from waitress import serve
import logging
import traceback

# Add the project directory to the Python path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

# Ensure log directory exists
LOG_DIR = r'C:\Users\Administrator\webapp'
LOG_FILE = os.path.join(LOG_DIR, 'django_service.log')
os.makedirs(LOG_DIR, exist_ok=True)

try:
    # Set up logging for debugging
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Logging initialized")
except Exception as e:
    # If we can't write to the log file, try writing to a temp file
    import tempfile
    temp_log = os.path.join(tempfile.gettempdir(), 'django_service_error.log')
    with open(temp_log, 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ERROR - Could not initialize logging: {str(e)}\n")
        f.write(traceback.format_exc())

class DjangoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DjangoWebService"
    _svc_display_name_ = "Django Web Service"
    _svc_description_ = "A Windows service running a Django web server using Waitress."

    def __init__(self, args):
        try:
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.running = True
            logging.info(f"Initializing Django service from {BASE_DIR}...")
        except Exception as e:
            self._log_exception("Error in service initialization", e)

    def _log_exception(self, message, exception):
        """Helper to log exceptions in multiple places for better visibility"""
        error_msg = f"{message}: {str(exception)}"
        logging.error(error_msg, exc_info=True)
        
        try:
            # Also log to Windows Event Log
            servicemanager.LogErrorMsg(error_msg)
        except:
            pass
            
        try:
            # Also log to a temp file as a last resort
            import tempfile
            temp_log = os.path.join(tempfile.gettempdir(), 'django_service_error.log')
            with open(temp_log, 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - ERROR - {error_msg}\n")
                f.write(traceback.format_exc())
        except:
            pass

    def SvcStop(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self.hWaitStop)
            self.running = False
            logging.info("Stopping Django service...")
        except Exception as e:
            self._log_exception("Error stopping service", e)

    def SvcDoRun(self):
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            logging.info("Service is running...")
            
            # Print working directory and Python path for debugging
            logging.info(f"Working directory: {os.getcwd()}")
            logging.info(f"Python path: {sys.path}")
            
            try:
                # Configure Django environment before any Django imports
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_requisition.settings')
                
                # For production, set DEBUG to False
                os.environ['DEBUG'] = 'False'
                
                # Print DJANGO_SETTINGS_MODULE for debugging
                logging.info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
                
                # Try to import Django first to catch any import errors
                logging.info("Importing Django...")
                import django
                logging.info(f"Django version: {django.__version__}")
                
                # Set up Django
                if not getattr(django, 'is_configured', False):
                    logging.info("Setting up Django...")
                    django.setup()
                
                # Import WSGI application after Django is configured
                from django.core.wsgi import get_wsgi_application
                
                logging.info("Initializing WSGI application...")
                self.application = get_wsgi_application()
                
                # Start Waitress to serve the application
                logging.info("Starting Waitress server on 0.0.0.0:8000...")
                serve(self.application, host='0.0.0.0', port=8000, threads=4)
                
            except ImportError as e:
                self._log_exception("Import error", e)
            except Exception as e:
                self._log_exception("Error setting up Django", e)
                
        except Exception as e:
            self._log_exception("Unhandled exception in SvcDoRun", e)

if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(DjangoService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(DjangoService)
    except Exception as e:
        # Last resort error handling for script execution
        error_msg = f"Fatal error in service main: {str(e)}"
        
        try:
            logging.error(error_msg, exc_info=True)
        except:
            pass
            
        try:
            # Write to a temp file that should always be writable
            import tempfile
            temp_log = os.path.join(tempfile.gettempdir(), 'django_service_error.log')
            with open(temp_log, 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - FATAL - {error_msg}\n")
                f.write(traceback.format_exc())
        except:
            pass