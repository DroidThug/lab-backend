@echo off
echo === Lab Requisition System Windows Server Setup ===
echo.

REM Check for administrator privileges
NET SESSION >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: This script requires administrator privileges.
    echo Please run as administrator.
    pause
    exit /b 1
)

echo Setting up environment variables...
setx DB_NAME "lab_requisition_db"
setx DB_USER "admin"
setx DB_PASSWORD "LETMEIN"
setx DB_HOST "localhost"
setx DB_PORT "5432"
setx DJANGO_SETTINGS_MODULE "lab_requisition.settings_prod"
echo Environment variables set.

echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo Creating static files directory...
mkdir staticfiles 2>nul

echo Collecting static files...
python manage.py collectstatic --noinput
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to collect static files.
)

echo Applying database migrations...
python manage.py migrate
if %ERRORLEVEL% neq 0 (
    echo Warning: Failed to apply migrations. Check your database configuration.
)

echo Installing and starting the Windows service...
python django_service.py install
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to install the Windows service.
    pause
    exit /b 1
)

echo Starting the service...
net start DjangoWebService
if %ERRORLEVEL% neq 0 (
    echo Error: Failed to start the Windows service.
    echo Check C:\Users\Administrator\webapp\django_service.log for details.
) else (
    echo Service started successfully.
)

echo.
echo === Installation Complete ===
echo Service Name: DjangoWebService
echo Log File: C:\Users\Administrator\webapp\django_service.log
echo.
echo Remember to update the settings_prod.py file with your actual domain name and security settings.
echo.

pause