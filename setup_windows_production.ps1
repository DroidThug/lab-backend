# setup_windows_production.ps1
# Run this script as Administrator to set up Django with Waitress and Nginx on Windows Server
param (
    [string]$ProjectPath = "C:\webapp\lab-backend",
    [string]$FrontendPath = "C:\webapp\lab-web",
    [string]$NginxPath = "C:\nginx",
    [string]$ApiDomain = "api.localhost",
    [string]$FrontendDomain = "localhost",
    [string]$StaticFilesPath = "C:\webapp\lab-backend\staticfiles",
    [string]$MediaFilesPath = "C:\webapp\lab-backend\media",
    [string]$FrontendBuildPath = "C:\webapp\lab-web\dist",
    [switch]$SkipFrontendBuild = $false
)

# Ensure we're running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script must be run as Administrator. Right-click PowerShell and select 'Run as Administrator'." -ForegroundColor Red
    exit
}

Write-Host "=== Setting up Django with Waitress and Nginx on Windows Server ===" -ForegroundColor Green

# Step 1: Create necessary directories
Write-Host "Creating necessary directories..."
$directories = @($ProjectPath, $StaticFilesPath, $MediaFilesPath, $FrontendPath)
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir"
    }
}

# Step 2: Set environment variables
Write-Host "Setting up environment variables..."
[Environment]::SetEnvironmentVariable("DJANGO_SETTINGS_MODULE", "lab_requisition.settings_prod", "Machine")
[Environment]::SetEnvironmentVariable("DEBUG", "False", "Machine")
[Environment]::SetEnvironmentVariable("DB_NAME", "lab_requisition_db", "Machine")
[Environment]::SetEnvironmentVariable("DB_USER", "admin", "Machine")
[Environment]::SetEnvironmentVariable("DB_PASSWORD", "LETMEIN", "Machine")
[Environment]::SetEnvironmentVariable("DB_HOST", "localhost", "Machine")
[Environment]::SetEnvironmentVariable("DB_PORT", "5432", "Machine")
[Environment]::SetEnvironmentVariable("ALLOWED_HOSTS", "$ApiDomain,$FrontendDomain", "Machine")

# Step 3: Install Nginx if not already installed
if (-not (Test-Path $NginxPath)) {
    Write-Host "Downloading and Installing Nginx..."
    $nginxDownloadUrl = "http://nginx.org/download/nginx-1.24.0.zip"
    $nginxZip = "$env:TEMP\nginx.zip"
    
    # Download Nginx
    Invoke-WebRequest -Uri $nginxDownloadUrl -OutFile $nginxZip
    
    # Extract to C:\nginx
    Expand-Archive -Path $nginxZip -DestinationPath "C:\" -Force
    Rename-Item -Path "C:\nginx-1.24.0" -NewName "C:\nginx" -Force
    
    # Clean up
    Remove-Item $nginxZip -Force
}

# Step 4: Configure Nginx
Write-Host "Configuring Nginx..."
$nginxConfigPath = "$NginxPath\conf\nginx.conf"
$nginxConfigContent = @"
worker_processes 1;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile      on;
    keepalive_timeout  65;
    
    # Static file handling
    include mime.types;
    
    # Additional MIME types for Vue.js apps
    types {
        application/javascript js mjs;
        application/json       json;
        text/css               css;
        image/svg+xml          svg;
    }
    
    # Gzip compression
    gzip on;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_types
        application/javascript
        application/json
        application/xml
        text/css
        text/plain
        text/xml
        image/svg+xml;
    
    # Django API Backend
    server {
        listen 80;
        server_name $ApiDomain;

        # Access and error logs
        access_log logs/django_access.log;
        error_log logs/django_error.log;

        # Django static files
        location /static/ {
            alias $($StaticFilesPath.Replace("\", "/"))/;
            expires 30d;
        }

        # Django media files
        location /media/ {
            alias $($MediaFilesPath.Replace("\", "/"))/;
            expires 30d;
        }

        # Proxy requests to Django/Waitress
        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
            proxy_connect_timeout 300s;
            proxy_read_timeout 300s;
            
            # Handle CORS preflight requests
            if (`$request_method = 'OPTIONS') {
                add_header 'Access-Control-Allow-Origin' '*';
                add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE';
                add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
                add_header 'Access-Control-Max-Age' 1728000;
                add_header 'Content-Type' 'text/plain; charset=utf-8';
                add_header 'Content-Length' 0;
                return 204;
            }
        }
    }
    
    # Vue.js Frontend Application
    server {
        listen 80;
        server_name $FrontendDomain;
        
        # Access and error logs
        access_log logs/vue_access.log;
        error_log logs/vue_error.log;
        
        root $($FrontendBuildPath.Replace("\", "/"));
        index index.html;
        
        # Serve static assets with proper cache control
        location /assets/ {
            expires 30d;
            add_header Cache-Control "public, max-age=2592000";
            try_files `$uri =404;
        }
        
        # Handle Single Page Application routing
        location / {
            try_files `$uri `$uri/ /index.html;
        }
    }
}
"@

Set-Content -Path $nginxConfigPath -Value $nginxConfigContent

# Step 5: Install Nginx as a Windows service using NSSM
Write-Host "Installing Nginx as a Windows service..."

# Download and extract NSSM if needed
$nssmPath = "$env:ProgramFiles\nssm"
if (-not (Test-Path "$nssmPath\nssm.exe")) {
    Write-Host "Downloading NSSM (Non-Sucking Service Manager)..."
    $nssmDownloadUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"
    
    # Create directory
    if (-not (Test-Path $nssmPath)) {
        New-Item -ItemType Directory -Path $nssmPath | Out-Null
    }
    
    # Download and extract
    Invoke-WebRequest -Uri $nssmDownloadUrl -OutFile $nssmZip
    Expand-Archive -Path $nssmZip -DestinationPath "$env:TEMP\nssm" -Force
    Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" -Destination "$nssmPath\nssm.exe" -Force
    
    # Clean up
    Remove-Item $nssmZip -Force
    Remove-Item "$env:TEMP\nssm" -Recurse -Force
}

# Remove existing Nginx service if it exists
$nginxService = Get-Service -Name "nginx" -ErrorAction SilentlyContinue
if ($nginxService) {
    Write-Host "Removing existing Nginx service..."
    & "$nssmPath\nssm.exe" remove nginx confirm
}

# Create Nginx service
Write-Host "Creating Nginx service..."
& "$nssmPath\nssm.exe" install nginx "$NginxPath\nginx.exe"
& "$nssmPath\nssm.exe" set nginx AppDirectory "$NginxPath"
& "$nssmPath\nssm.exe" set nginx DisplayName "Nginx Web Server"
& "$nssmPath\nssm.exe" set nginx Description "Nginx web server for Django application and Vue.js frontend"
& "$nssmPath\nssm.exe" set nginx AppStdout "$NginxPath\logs\service-stdout.log"
& "$nssmPath\nssm.exe" set nginx AppStderr "$NginxPath\logs\service-stderr.log"
& "$nssmPath\nssm.exe" set nginx Start SERVICE_AUTO_START

# Step 6: Create a waitress_server.py script
Write-Host "Creating Waitress server script..."
$waitressScriptPath = "$ProjectPath\waitress_server.py"
$waitressScriptContent = @"
import os
import sys
import logging
from waitress import serve

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename='$ProjectPath\waitress.log',
    filemode='a'
)

# Add the project directory to the Python path
sys.path.insert(0, '$ProjectPath')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab_requisition.settings_prod')

logging.info('Starting Waitress server...')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    logging.info('Django WSGI application loaded successfully')
    
    # Start Waitress server
    serve(
        application,
        host='0.0.0.0',
        port=8000,
        threads=4,
        url_scheme='http'
    )
except Exception as e:
    logging.error(f'Error starting server: {str(e)}', exc_info=True)
    sys.exit(1)
"@

Set-Content -Path $waitressScriptPath -Value $waitressScriptContent

# Step 7: Install Django Waitress as a Windows service
Write-Host "Installing Django Waitress as a Windows service..."

# Remove existing Django service if it exists
$djangoService = Get-Service -Name "DjangoService" -ErrorAction SilentlyContinue
if ($djangoService) {
    Write-Host "Removing existing Django service..."
    & "$nssmPath\nssm.exe" remove DjangoService confirm
}

# Create Django service
Write-Host "Creating Django service..."
$pythonExe = (Get-Command python).Source
& "$nssmPath\nssm.exe" install DjangoService "$pythonExe"
& "$nssmPath\nssm.exe" set DjangoService AppParameters "$waitressScriptPath"
& "$nssmPath\nssm.exe" set DjangoService AppDirectory "$ProjectPath"
& "$nssmPath\nssm.exe" set DjangoService DisplayName "Django Waitress Service"
& "$nssmPath\nssm.exe" set DjangoService Description "Django web application running with Waitress"
& "$nssmPath\nssm.exe" set DjangoService AppStdout "$ProjectPath\django_service_stdout.log"
& "$nssmPath\nssm.exe" set DjangoService AppStderr "$ProjectPath\django_service_stderr.log"
& "$nssmPath\nssm.exe" set DjangoService Start SERVICE_AUTO_START

# Step 8: Collect static files for Django
Write-Host "Collecting static files..."
Set-Location -Path $ProjectPath
python manage.py collectstatic --noinput --settings=lab_requisition.settings_prod

# Step 9: Build Vue.js Frontend (if not skipped)
if (-not $SkipFrontendBuild) {
    Write-Host "Setting up Vue.js frontend..."
    $apiUrl = "http://$ApiDomain"
    
    # Check if Node.js is installed
    try {
        $nodeVersion = node -v
        Write-Host "Node.js is installed: $nodeVersion"
        
        # Set up and build the Vue.js application
        Write-Host "Building Vue.js application..."
        Set-Location -Path $FrontendPath
        
        # Create production environment variables file
        @"
VITE_API_URL=$apiUrl
VITE_NODE_ENV=production
"@ | Out-File -FilePath "$FrontendPath\.env.production" -Encoding utf8 -Force
        
        # Install dependencies and build
        npm install
        npm run build
        
        # Check if build was successful
        if (Test-Path "$FrontendPath\dist") {
            Write-Host "Vue.js build successful."
        } else {
            Write-Host "Vue.js build failed. Make sure your frontend code is complete and error-free." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Node.js not found. Skipping Vue.js build." -ForegroundColor Yellow
        Write-Host "Please install Node.js and run the setup_vuejs_frontend.ps1 script separately." -ForegroundColor Yellow
    }
}

# Step 10: Start services
Write-Host "Starting services..."
Start-Service DjangoService
Start-Service nginx

# Done!
Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "Django application is now running with Waitress and Nginx on Windows Server"
Write-Host "API endpoint: http://$ApiDomain"
Write-Host "Frontend: http://$FrontendDomain"
Write-Host "`nService management:"
Write-Host "  - Start services:   Start-Service DjangoService; Start-Service nginx"
Write-Host "  - Stop services:    Stop-Service DjangoService; Stop-Service nginx"
Write-Host "  - Restart services: Restart-Service DjangoService; Restart-Service nginx"
Write-Host "`nLog files:"
Write-Host "  - Django Waitress logs: $ProjectPath\waitress.log"
Write-Host "  - Django service logs:  $ProjectPath\django_service_stdout.log"
Write-Host "  - Nginx access logs:    $NginxPath\logs\django_access.log"
Write-Host "  - Nginx error logs:     $NginxPath\logs\django_error.log"
Write-Host "  - Vue.js access logs:   $NginxPath\logs\vue_access.log"
Write-Host "`nDon't forget to update the domain names in lab_requisition/settings_prod.py's ALLOWED_HOSTS setting!"