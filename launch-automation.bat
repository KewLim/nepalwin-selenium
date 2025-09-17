@echo off
REM Terminal Automation Launcher with Custom Settings
REM This script opens a new terminal with custom size and font settings

echo ====================================================
echo           SELENIUM AUTOMATION LAUNCHER
echo ====================================================
echo.
echo Select which automation to run:
echo 1. Deposit Crawler
echo 2. Phone Number Crawler
echo 3. Balance Crawler
echo 4. Add Deposit
echo 5. Add Player
echo.
set /p choice="Enter your choice (1-5): "

REM Clear screen and set terminal properties
cls
title Selenium Automation - Running...

REM Set terminal size (columns x rows) - adjust as needed
mode con cols=120 lines=40

echo.
echo Starting automation with custom terminal settings...
echo Terminal size: 120x40
echo.

if "%choice%"=="1" (
    echo Running Deposit Crawler...
    python selenium-crawler-depo.py
) else if "%choice%"=="2" (
    echo Running Phone Number Crawler...
    python selenium-crawler-phone.py
) else if "%choice%"=="3" (
    echo Running Balance Crawler...
    python selenium-crawler-balance.py
) else if "%choice%"=="4" (
    echo Running Add Deposit...
    python selenium-add-deposit.py
) else if "%choice%"=="5" (
    echo Running Add Player...
    python selenium-add-player.py
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit
)

echo.
echo ====================================================
echo           AUTOMATION COMPLETED
echo ====================================================
pause