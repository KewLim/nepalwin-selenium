@echo off
REM Simple Batch Launcher - Opens Each Automation in NEW CMD Window
title Selenium Automation Launcher

cls
echo ====================================================
echo           SELENIUM AUTOMATION LAUNCHER
echo           (NEW WINDOW MODE)
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

echo.
echo Opening new terminal window...

if "%choice%"=="1" (
    start "Selenium - Deposit Crawler" cmd /k "mode con cols=120 lines=40 && title Selenium - Deposit Crawler && cls && echo ==== DEPOSIT CRAWLER ==== && python selenium-crawler-depo.py && echo. && echo ==== COMPLETED ==== && pause"
) else if "%choice%"=="2" (
    start "Selenium - Phone Crawler" cmd /k "mode con cols=120 lines=40 && title Selenium - Phone Crawler && cls && echo ==== PHONE NUMBER CRAWLER ==== && python selenium-crawler-phone.py && echo. && echo ==== COMPLETED ==== && pause"
) else if "%choice%"=="3" (
    start "Selenium - Balance Crawler" cmd /k "mode con cols=120 lines=40 && title Selenium - Balance Crawler && cls && echo ==== BALANCE CRAWLER ==== && python selenium-crawler-balance.py && echo. && echo ==== COMPLETED ==== && pause"
) else if "%choice%"=="4" (
    start "Selenium - Add Deposit" cmd /k "mode con cols=120 lines=40 && title Selenium - Add Deposit && cls && echo ==== ADD DEPOSIT ==== && python selenium-add-deposit.py && echo. && echo ==== COMPLETED ==== && pause"
) else if "%choice%"=="5" (
    start "Selenium - Add Player" cmd /k "mode con cols=120 lines=40 && title Selenium - Add Player && cls && echo ==== ADD PLAYER ==== && python selenium-add-player.py && echo. && echo ==== COMPLETED ==== && pause"
) else (
    echo Invalid choice. Please try again.
    pause
    goto :eof
)

echo.
echo ✅ New terminal window opened!
echo 📝 You can close this launcher now.
echo.
pause