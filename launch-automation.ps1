# PowerShell Terminal Automation Launcher with Enhanced Customization
# This script provides better terminal control than batch files

# Function to create a new terminal window with custom settings
function Start-AutomationWithCustomTerminal {
    param(
        [string]$ScriptName,
        [int]$Width = 120,
        [int]$Height = 40,
        [int]$FontSize = 11
    )

    # Create command string with proper variable substitution
    $command = @"
        # Set console properties
        `$host.UI.RawUI.WindowSize = New-Object System.Management.Automation.Host.Size($Width, $Height)
        `$host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size($Width, 1000)

        # Clear the screen
        Clear-Host

        # Set window title
        `$host.UI.RawUI.WindowTitle = 'Selenium Automation - $ScriptName'

        # Display header
        Write-Host '====================================================' -ForegroundColor Green
        Write-Host '           SELENIUM AUTOMATION LAUNCHER' -ForegroundColor Green
        Write-Host '           Running: $ScriptName' -ForegroundColor Yellow
        Write-Host '           Terminal: ${Width}x${Height} | Font: ${FontSize}pt' -ForegroundColor Cyan
        Write-Host '====================================================' -ForegroundColor Green
        Write-Host ''

        # Run the Python script
        & python '$ScriptName'

        # Keep window open
        Write-Host ''
        Write-Host '====================================================' -ForegroundColor Green
        Write-Host '           AUTOMATION COMPLETED' -ForegroundColor Green
        Write-Host '====================================================' -ForegroundColor Green
        Read-Host 'Press Enter to close this window'
"@

    # Create new PowerShell window with custom settings
    $arguments = @(
        "-NoExit"
        "-Command"
        $command
    )

    Start-Process "powershell.exe" -ArgumentList $arguments
}

# Clear current terminal
Clear-Host

# Display menu
Write-Host "====================================================" -ForegroundColor Green
Write-Host "           SELENIUM AUTOMATION LAUNCHER" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Select which automation to run:" -ForegroundColor Yellow
Write-Host "1. Phone Number Crawler" -ForegroundColor White
Write-Host "2. Deposit Crawler" -ForegroundColor White
Write-Host "3. Add Player" -ForegroundColor White
Write-Host "4. Add Deposit" -ForegroundColor White
Write-Host ""
Write-Host "Terminal Customization Options:" -ForegroundColor Cyan
Write-Host "- Window Size: 120x40 characters" -ForegroundColor Gray
Write-Host "- Font Size: 12pt (adjustable in script)" -ForegroundColor Gray
Write-Host "- Fresh terminal window for each run" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "Launching Phone Number Crawler in new terminal..." -ForegroundColor Green
        Start-AutomationWithCustomTerminal -ScriptName "selenium-crawler-phone.py"
    }
    "2" {
        Write-Host "Launching Deposit Crawler in new terminal..." -ForegroundColor Green
        Start-AutomationWithCustomTerminal -ScriptName "selenium-crawler-depo.py"
    }
    "3" {
        Write-Host "Launching Add Player in new terminal..." -ForegroundColor Green
        Start-AutomationWithCustomTerminal -ScriptName "selenium-add-player.py"
    }
    "4" {
        Write-Host "Launching Add Deposit in new terminal..." -ForegroundColor Green
        Start-AutomationWithCustomTerminal -ScriptName "selenium-add-deposit.py"
    }
    default {
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
        Read-Host "Press Enter to exit"
    }
}

# Instructions for font size customization
Write-Host ""
Write-Host "To customize font size:" -ForegroundColor Yellow
Write-Host "Edit this PowerShell script and change the FontSize parameter in Start-AutomationWithCustomTerminal function" -ForegroundColor Gray