@echo off
setlocal

cd /d "%~dp0"
echo [1/2] Installing/Updating build tools...
python -m pip install --upgrade pip pyinstaller

echo [2/2] Building Icon QR exe...
if exist "IconQR.exe" del /f /q "IconQR.exe"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "IconQR.spec" del /f /q "IconQR.spec"

pyinstaller ^
  --noconfirm ^
  --clean ^
  --name IconQR ^
  --onefile ^
  --windowed ^
  --distpath "." ^
  --add-data "templates;templates" ^
  --add-data "icon.png;." ^
  desktop_launcher.py

if errorlevel 1 (
  echo.
  echo Build failed.
  pause
  exit /b 1
)

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "IconQR.spec" del /f /q "IconQR.spec"

echo.
echo Build finished.
echo Run: IconQR.exe
echo.
pause
