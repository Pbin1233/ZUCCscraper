@echo off

:: Get the current date components
for /f "tokens=2 delims==" %%I in ('"wmic path win32_localtime get dayofweek /value"') do set DOW=%%I
for /f "tokens=2 delims==" %%I in ('"wmic path win32_localtime get day /value"') do set DAY=%%I
for /f "tokens=2 delims==" %%I in ('"wmic path win32_localtime get month /value"') do set MONTH=%%I
for /f "tokens=2 delims==" %%I in ('"wmic path win32_localtime get year /value"') do set YEAR=%%I

:: Calculate the last day of the month
set /a nextMonth=MONTH %% 12 + 1
set /a nextYear=YEAR + (MONTH == 12 ? 1 : 0)

:: Use PowerShell to find the last day of the month
for /f %%I in ('"powershell -command (New-Object DateTime %YEAR%,%nextMonth%,1).AddDays(-1).Day"') do set LASTDAY=%%I

:: Calculate the day difference from the end of the month
set /a DIFF=LASTDAY - DAY

SET LOG_LEVEL=INFO

:: Check if today is within the last three days of the month
if %DIFF% lss 3 (
    echo Running the Python script because it is within the last three days of the month.
    python "%~dp0main.py" true
) else (
    echo Not the last three days of the month. Exiting.
    python "%~dp0main.py" true
)
exit
