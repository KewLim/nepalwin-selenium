# Enhanced PowerShell Launcher - Opens Each Automation in NEW Terminal Window
# This script ensures each automation runs in a completely fresh terminal

# Function to launch automation in a brand new terminal window
function Start-AutomationInNewTerminal {
    param(
        [string]$ScriptName,
        [int]$Width = 120,
        [int]$Height = 40,
        [int]$FontSize = 11
    )

    # Create a temporary batch file to launch the automation with proper terminal settings
    $tempBatchFile = "temp_launcher_$(Get-Random).bat"
    $currentPath = Get-Location

    $batchContent = @"
@echo off
title Selenium Automation - $ScriptName
mode con cols=$Width lines=$Height
cd /d "$currentPath"
cls
echo ====================================================
echo           SELENIUM AUTOMATION - $ScriptName
echo           Terminal: ${Width}x${Height} ^| Font: ${FontSize}pt
echo ====================================================
echo.
python "$ScriptName"
echo.
echo ====================================================
echo           AUTOMATION COMPLETED
echo ====================================================
pause
del "%~f0"
"@

    # Write the batch file
    $batchContent | Out-File -FilePath $tempBatchFile -Encoding ASCII

    # Launch in new command prompt window
    Start-Process "cmd.exe" -ArgumentList "/c", $tempBatchFile -WindowStyle Normal

    Write-Host "✅ Launched $ScriptName in new terminal window" -ForegroundColor Green
}

# Alternative function using Windows Terminal (if available)
function Start-AutomationInWindowsTerminal {
    param(
        [string]$ScriptName,
        [int]$Width = 120,
        [int]$Height = 40,
        [int]$FontSize = 11
    )

    try {
        # Check if Windows Terminal is available
        $wtPath = Get-Command "wt.exe" -ErrorAction SilentlyContinue

        if ($wtPath) {
            $currentPath = Get-Location
            $command = "cmd.exe /k `"cd /d $currentPath && mode con cols=$Width lines=$Height && title Selenium Automation - $ScriptName && cls && echo ================================================== && echo           SELENIUM AUTOMATION - $ScriptName && echo           Terminal: ${Width}x${Height} ^| Font: ${FontSize}pt && echo ================================================== && echo. && python $ScriptName && echo. && echo ================================================== && echo           AUTOMATION COMPLETED && echo ================================================== && pause`""

            Start-Process "wt.exe" -ArgumentList "new-tab", "--title", "Selenium - $ScriptName", $command
            Write-Host "✅ Launched $ScriptName in Windows Terminal" -ForegroundColor Green
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

# Clear current terminal
Clear-Host

# Display enhanced menu
Write-Host "====================================================" -ForegroundColor Green
Write-Host "           SELENIUM AUTOMATION LAUNCHER" -ForegroundColor Green
Write-Host "           (NEW TERMINAL WINDOW MODE)" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Select which automation to run:" -ForegroundColor Yellow
Write-Host "1. Deposit Crawler" -ForegroundColor White
Write-Host "2. Phone Number Crawler" -ForegroundColor White
Write-Host "3. Balance Crawler" -ForegroundColor White
Write-Host "4. Add Deposit" -ForegroundColor White
Write-Host "5. Add Player" -ForegroundColor White
Write-Host ""
Write-Host "Terminal Settings:" -ForegroundColor Cyan
Write-Host "- Window Size: 120x40 characters" -ForegroundColor Gray
Write-Host "- Font Size: 11pt" -ForegroundColor Gray
Write-Host "- Each run opens in a FRESH new window" -ForegroundColor Gray
Write-Host "- Previous terminal sessions won't interfere" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

Write-Host ""
Write-Host "Launching automation in new terminal window..." -ForegroundColor Yellow

switch ($choice) {
    "1" {
        if (-not (Start-AutomationInWindowsTerminal -ScriptName "selenium-crawler-depo.py")) {
            Start-AutomationInNewTerminal -ScriptName "selenium-crawler-depo.py"
        }
    }
    "2" {
        if (-not (Start-AutomationInWindowsTerminal -ScriptName "selenium-crawler-phone.py")) {
            Start-AutomationInNewTerminal -ScriptName "selenium-crawler-phone.py"
        }
    }
    "3" {
        if (-not (Start-AutomationInWindowsTerminal -ScriptName "selenium-crawler-balance.py")) {
            Start-AutomationInNewTerminal -ScriptName "selenium-crawler-balance.py"
        }
    }
    "4" {
        if (-not (Start-AutomationInWindowsTerminal -ScriptName "selenium-add-deposit.py")) {
            Start-AutomationInNewTerminal -ScriptName "selenium-add-deposit.py"
        }
    }
    "5" {
        if (-not (Start-AutomationInWindowsTerminal -ScriptName "selenium-add-player.py")) {
            Start-AutomationInNewTerminal -ScriptName "selenium-add-player.py"
        }
    }
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit
    }
}

Write-Host ""
Write-Host "🎯 New terminal window opened!" -ForegroundColor Green
Write-Host "📝 Note: You can close this launcher window now." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to close this launcher"