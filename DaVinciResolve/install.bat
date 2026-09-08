@echo off
cd /d "%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\" || (
  echo DaVinci Resolve Scripts not found: "%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\"
  exit /b 1
)
@echo off
rem Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo Restarting with admin rights...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -ArgumentList 'elevated'"
  exit /b
)

rem Define target and source paths
set "target=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Comp\Title.py"
set "source=%~dp0Title.py"

if exist "%target%" (
  echo target exists, deleting and recreating...
  del /f "%target%" >nul 2>&1
)

rem Create symbolic link
mklink "%target%" "%source%"
if %errorlevel% neq 0 (
  echo Failed to create symbolic link.
  exit /b 1
)

