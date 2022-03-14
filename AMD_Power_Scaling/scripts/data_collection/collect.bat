::===============================================================
:: PowerShell Script to collect User Data for Windows
:: Currently collecting Battery Info
::===============================================================

@echo off

if "%1%"=="" (
    echo Invalid Parameters -- try "/help" for help
    exit 0
)

if %1%==/help (
    echo Usage
    echo   ./collect.bat directory days seconds
    echo.
    echo Help
    echo   /help           Help Options
    echo.
    echo Arguments
    echo   directory       str: directory to store data reports in
    echo   days            int: number of days of history needed to generate reports
    echo   seconds         int: number of seconds of history needed to generate energy report 
    echo.
    echo If you get permission denied: run PowerShell as Administrator
    echo.
    echo Report bugs to Shamith Achanta ^<shamith2@illinois.edu^>
    exit 0
)

echo Welcome to AMD Power Scaling Data Collection for Windows Users
echo Copyright (c) 2022 Shamith Achanta
echo.
echo The following system data will be collected: MEMORY USAGE, CPU USAGE, GPU USAGE, BATTERY HEALTH
echo.
echo Do you wish to continue. If so, your identity will be anonymous.
set /p to_continue="Enter [y] or n to continue... "

if "%to_continue%"=="n" (
    echo Thank you. Exiting...
    echo.
    echo Have a Great Day!!!
    exit 0
)

if "%to_continue%"=="N" (
    echo Thank you. Exiting...
    echo.
    echo Have a Great Day!!!
    exit 0
)

if not exist %1\ (
    mkdir %1\
)

echo Generating Battery Report for duration %2 days...
powercfg /batteryreport /duration %2 /output %1\battery-report.xml /xml
echo Done generating Battery Report
echo.

echo Generating Energy Report for duration %3 seconds...
powercfg /energy /duration %3 /output %1\energy-report.xml /xml
echo Done generating Energy Report
echo.

echo Generating Power Report for duration %2 days...
powercfg /systempowerreport /duration %2 /output %1\power-report.xml /xml
echo Done generating Power Report
echo.

exit 0
