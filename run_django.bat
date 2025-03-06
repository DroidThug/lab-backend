@echo off
echo Starting Django application with Waitress...
echo.

set DJANGO_SETTINGS_MODULE=lab_requisition.settings_prod
set DEBUG=False

python -c "import os, sys; sys.path.insert(0, os.path.abspath('.')); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_requisition.settings_prod'); from waitress import serve; from django.core.wsgi import get_wsgi_application; serve(get_wsgi_application(), host='0.0.0.0', port=8000)"

echo.
if %ERRORLEVEL% NEQ 0 (
    echo Error starting Django application. See error message above.
    pause
) else (
    echo Django application stopped.
    pause
)