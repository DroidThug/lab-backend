# setup_vuejs_frontend.ps1
# This script builds and deploys the Vue.js frontend application
param (
    [string]$FrontendPath = "C:\webapp\lab-web",
    [string]$ApiUrl = "http://api.localhost",
    [string]$BuildOutputPath = "C:\webapp\lab-web\dist"
)

Write-Host "=== Setting up Vue.js Frontend Application ===" -ForegroundColor Green

# Step 1: Ensure Node.js is installed
try {
    $nodeVersion = node -v
    Write-Host "Node.js is installed: $nodeVersion"
}
catch {
    Write-Host "Node.js is not installed. Please install Node.js before proceeding." -ForegroundColor Red
    Write-Host "Download from: https://nodejs.org/en/download/" -ForegroundColor Yellow
    exit 1
}

# Step 2: Install required npm packages
Write-Host "Installing npm dependencies..."
Set-Location -Path $FrontendPath
npm install

# Step 3: Create or update .env file with production API URL
Write-Host "Configuring production API endpoint..."
@"
VITE_API_URL=$ApiUrl
VITE_NODE_ENV=production
"@ | Out-File -FilePath "$FrontendPath\.env.production" -Encoding utf8 -Force

# Step 4: Build the Vue.js application
Write-Host "Building Vue.js application for production..."
npm run build

# Step 5: Ensure the dist directory exists
if (-not (Test-Path "$FrontendPath\dist")) {
    Write-Host "Error: Build failed or dist directory was not created." -ForegroundColor Red
    exit 1
}

Write-Host "Vue.js application built successfully." -ForegroundColor Green

# Step 6: Copy the built files to the deployment location (if different)
if ($BuildOutputPath -ne "$FrontendPath\dist") {
    Write-Host "Copying built files to deployment location..."
    
    # Create directory if it doesn't exist
    if (-not (Test-Path $BuildOutputPath)) {
        New-Item -ItemType Directory -Path $BuildOutputPath | Out-Null
    }
    
    # Copy all files from dist to deployment location
    Copy-Item -Path "$FrontendPath\dist\*" -Destination $BuildOutputPath -Recurse -Force
}

Write-Host "`n=== Vue.js Frontend Setup Complete! ===" -ForegroundColor Green
Write-Host "Frontend files are located at: $BuildOutputPath"
Write-Host "The application is configured to use API at: $ApiUrl"

# Provide instructions for Nginx configuration
Write-Host "`nMake sure your Nginx is configured with:"
Write-Host "  - Server block pointing to: $BuildOutputPath"
Write-Host "  - SPA routing: try_files \$uri \$uri/ /index.html;"