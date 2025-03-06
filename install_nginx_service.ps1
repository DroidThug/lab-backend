# Install-NginxService.ps1
# Run this script as Administrator

# Define the path to the Nginx installation
$nginxPath = "C:\nginx"

# Import the necessary modules for Windows services
Add-Type -AssemblyName System.ServiceProcess

# Check if the service already exists
$service = Get-Service -Name "nginx" -ErrorAction SilentlyContinue
if ($service -ne $null) {
    Write-Host "Nginx service already exists."
    exit
}

# Download the nssm service manager if needed
$nssmPath = "$env:ProgramFiles\nssm"
if (-not (Test-Path "$nssmPath\nssm.exe")) {
    Write-Host "Downloading NSSM (Non-Sucking Service Manager)..."
    $nssmDownloadUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"
    
    # Create the directory if it doesn't exist
    if (-not (Test-Path $nssmPath)) {
        New-Item -ItemType Directory -Path $nssmPath | Out-Null
    }
    
    # Download and extract NSSM
    Invoke-WebRequest -Uri $nssmDownloadUrl -OutFile $nssmZip
    Expand-Archive -Path $nssmZip -DestinationPath "$env:TEMP\nssm" -Force
    Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" -Destination "$nssmPath\nssm.exe" -Force
    
    # Clean up temporary files
    Remove-Item $nssmZip -Force
    Remove-Item "$env:TEMP\nssm" -Recurse -Force
}

# Add nssm to the PATH if it's not already there
$env:Path = "$env:Path;$nssmPath"
[Environment]::SetEnvironmentVariable("Path", $env:Path, "Machine")

# Create the Nginx service using nssm
Write-Host "Creating Nginx service..."
& "$nssmPath\nssm.exe" install nginx "$nginxPath\nginx.exe"
& "$nssmPath\nssm.exe" set nginx AppParameters ""
& "$nssmPath\nssm.exe" set nginx DisplayName "Nginx Web Server"
& "$nssmPath\nssm.exe" set nginx Description "Nginx web server for serving web applications"
& "$nssmPath\nssm.exe" set nginx Start SERVICE_AUTO_START
& "$nssmPath\nssm.exe" set nginx AppStdout "$nginxPath\logs\service-stdout.log"
& "$nssmPath\nssm.exe" set nginx AppStderr "$nginxPath\logs\service-stderr.log"

# Configure the working directory
& "$nssmPath\nssm.exe" set nginx AppDirectory "$nginxPath"

# Start the service
Start-Service -Name "nginx"

Write-Host "Nginx service installed and started successfully."
Write-Host "You can manage it using the standard Windows service commands:"
Write-Host "  - Start-Service nginx"
Write-Host "  - Stop-Service nginx"
Write-Host "  - Restart-Service nginx"
Write-Host "Nginx configuration file is located at: $nginxPath\conf\nginx.conf"