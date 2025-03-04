import os
import sys
import time
import win32service
import win32serviceutil
import win32event
import servicemanager
from waitress import serve
import logging

# Add the project directory to the Python path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

# Set up logging for debugging
LOG_FILE = r'C:\Users\Administrator\webapp\django_service.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DjangoService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DjangoWebService"
    _svc_display_name_ = "Django Web Service"
    _svc_description_ = "A Windows service running a Django web server using Waitress."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        logging.info(f"Initializing Django service from {BASE_DIR}...")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False
        logging.info("Stopping Django service...")

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        logging.info("Service is running...")
        logging.info(f"Python path: {sys.path}")
        
        try:
            # Configure Django environment
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_requisition.settings')
            
            # For production, set DEBUG to False
            os.environ['DEBUG'] = 'False'
            
            # Import Django modules after environment is set
            from django.core.wsgi import get_wsgi_application
            
            # Allow some time for initialization before getting the WSGI application
            time.sleep(2)
            
            logging.info("Initializing WSGI application...")
            self.application = get_wsgi_application()
            
            # Start Waitress to serve the application
            logging.info("Starting Waitress server...")
            serve(self.application, host='0.0.0.0', port=8000, threads=4)
            
        except Exception as e:
            logging.error(f"Error in service: {str(e)}", exc_info=True)
            servicemanager.LogErrorMsg(f"Error in service: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DjangoService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DjangoService)