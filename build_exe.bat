@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "APP_NAME=IconQR"
set "EXE_NAME=%APP_NAME%.exe"
set "WORKPATH=%CD%\.pyi_build"
set "SPECPATH=%CD%\.pyi_spec"
set "DISTPATH=%CD%\.pyi_dist"
set "DIST_EXE=%DISTPATH%\%EXE_NAME%"
set "TEMPLATES_SRC=%CD%\templates"
set "FAVICON_SRC=%CD%\images\favicon.ico"
set "ICON_SRC=%CD%\icon.png"
set "PYTHON_EXE="
set "PYTHON_ARGS="
set "VENV_HOME="
set "PY_BASE="
set "FFI_SRC="

if exist "%CD%\.venv\pyvenv.cfg" (
  for /f "tokens=1,* delims==" %%A in ('findstr /b /c:"home =" "%CD%\.venv\pyvenv.cfg" 2^>nul') do set "VENV_HOME=%%B"
)
if defined VENV_HOME (
  set "VENV_HOME=%VENV_HOME:~1%"
  if exist "%VENV_HOME%\python.exe" set "PYTHON_EXE=%VENV_HOME%\python.exe"
)
if not defined PYTHON_EXE if exist "%USERPROFILE%\miniconda3\python.exe" set "PYTHON_EXE=%USERPROFILE%\miniconda3\python.exe"
if not defined PYTHON_EXE if exist "%CD%\.venv\Scripts\python.exe" set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
if not defined PYTHON_EXE if exist "%SystemRoot%\py.exe" (
  set "PYTHON_EXE=%SystemRoot%\py.exe"
  set "PYTHON_ARGS=-3"
)
if not defined PYTHON_EXE (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_EXE=python"
)
if not defined PYTHON_EXE goto :python_not_found

if /i "%PYTHON_EXE%"=="python" (
  set "PY_BASE="
) else (
  for %%I in ("%PYTHON_EXE%") do set "PY_BASE=%%~dpI"
)
if defined PY_BASE if exist "%PY_BASE%\Library\bin\ffi.dll" set "FFI_SRC=%PY_BASE%\Library\bin\ffi.dll"
if not defined FFI_SRC if exist "%USERPROFILE%\miniconda3\Library\bin\ffi.dll" set "FFI_SRC=%USERPROFILE%\miniconda3\Library\bin\ffi.dll"
if not defined FFI_SRC if exist "C:\Users\ISL_CJY\miniconda3\Library\bin\ffi.dll" set "FFI_SRC=C:\Users\ISL_CJY\miniconda3\Library\bin\ffi.dll"

echo [0/3] Closing running Icon QR...
taskkill /IM "%EXE_NAME%" /F >nul 2>nul

echo [1/3] Installing/Updating build tools...
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --upgrade pip pyinstaller
if errorlevel 1 goto :build_failed

if exist "%WORKPATH%" rmdir /s /q "%WORKPATH%"
if exist "%SPECPATH%" rmdir /s /q "%SPECPATH%"
if exist "%DISTPATH%" rmdir /s /q "%DISTPATH%"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "%APP_NAME%.spec" del /f /q "%APP_NAME%.spec"

echo [2/3] Building Icon QR exe...
mkdir "%WORKPATH%" >nul 2>nul
mkdir "%SPECPATH%" >nul 2>nul
mkdir "%DISTPATH%" >nul 2>nul

if defined FFI_SRC (
  "%PYTHON_EXE%" %PYTHON_ARGS% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --name %APP_NAME% ^
    --onefile ^
    --windowed ^
    --icon "%FAVICON_SRC%" ^
    --distpath "%DISTPATH%" ^
    --workpath "%WORKPATH%" ^
    --specpath "%SPECPATH%" ^
    --add-binary "%FFI_SRC%;." ^
    --add-data "%TEMPLATES_SRC%;templates" ^
    --add-data "%FAVICON_SRC%;images" ^
    --add-data "%ICON_SRC%;." ^
    desktop_launcher.py
) else (
  "%PYTHON_EXE%" %PYTHON_ARGS% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --name %APP_NAME% ^
    --onefile ^
    --windowed ^
    --icon "%FAVICON_SRC%" ^
    --distpath "%DISTPATH%" ^
    --workpath "%WORKPATH%" ^
    --specpath "%SPECPATH%" ^
    --add-data "%TEMPLATES_SRC%;templates" ^
    --add-data "%FAVICON_SRC%;images" ^
    --add-data "%ICON_SRC%;." ^
    desktop_launcher.py
)

if errorlevel 1 (
  echo Build attempt 1 failed. Retrying once...
  timeout /t 1 /nobreak >nul
  if exist "%WORKPATH%" rmdir /s /q "%WORKPATH%"
  if exist "%SPECPATH%" rmdir /s /q "%SPECPATH%"
  if exist "%DISTPATH%" rmdir /s /q "%DISTPATH%"
  mkdir "%WORKPATH%" >nul 2>nul
  mkdir "%SPECPATH%" >nul 2>nul
  mkdir "%DISTPATH%" >nul 2>nul

  if defined FFI_SRC (
    "%PYTHON_EXE%" %PYTHON_ARGS% -m PyInstaller ^
      --noconfirm ^
      --clean ^
      --name %APP_NAME% ^
      --onefile ^
      --windowed ^
      --icon "%FAVICON_SRC%" ^
      --distpath "%DISTPATH%" ^
      --workpath "%WORKPATH%" ^
      --specpath "%SPECPATH%" ^
      --add-binary "%FFI_SRC%;." ^
      --add-data "%TEMPLATES_SRC%;templates" ^
      --add-data "%FAVICON_SRC%;images" ^
      --add-data "%ICON_SRC%;." ^
      desktop_launcher.py
  ) else (
    "%PYTHON_EXE%" %PYTHON_ARGS% -m PyInstaller ^
      --noconfirm ^
      --clean ^
      --name %APP_NAME% ^
      --onefile ^
      --windowed ^
      --icon "%FAVICON_SRC%" ^
      --distpath "%DISTPATH%" ^
      --workpath "%WORKPATH%" ^
      --specpath "%SPECPATH%" ^
      --add-data "%TEMPLATES_SRC%;templates" ^
      --add-data "%FAVICON_SRC%;images" ^
      --add-data "%ICON_SRC%;." ^
      desktop_launcher.py
  )

  if errorlevel 1 goto :build_failed
)

if not exist "%DIST_EXE%" goto :build_failed

taskkill /IM "%EXE_NAME%" /F >nul 2>nul
set "COPY_OK=0"
for /l %%I in (1,1,10) do (
  if exist "%EXE_NAME%" del /f /q "%EXE_NAME%" >nul 2>nul
  copy /y "%DIST_EXE%" "%EXE_NAME%" >nul 2>nul
  if exist "%EXE_NAME%" (
    set "COPY_OK=1"
    goto :copy_done
  )
  timeout /t 1 /nobreak >nul
)

:copy_done
if not "%COPY_OK%"=="1" goto :build_failed

if exist "%WORKPATH%" rmdir /s /q "%WORKPATH%"
if exist "%SPECPATH%" rmdir /s /q "%SPECPATH%"
if exist "%DISTPATH%" rmdir /s /q "%DISTPATH%"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "%APP_NAME%.spec" del /f /q "%APP_NAME%.spec"

echo.
echo Build finished.
echo Run: %EXE_NAME%
echo.
pause
exit /b 0

:python_not_found
echo.
echo Build failed.
echo Python interpreter not found.
echo Install Python or create .venv, then run build_exe.bat again.
echo.
pause
exit /b 1

:build_failed
echo.
echo Build failed.
echo Please close IconQR.exe and try again.
echo.
pause
exit /b 1
