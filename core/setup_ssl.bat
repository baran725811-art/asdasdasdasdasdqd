@echo off
REM SSL Certificate Setup Script for Windows
REM This script creates trusted SSL certificates for local development

echo ========================================
echo SSL Certificate Setup for Development
echo ========================================
echo.

REM Check if mkcert is installed
where mkcert >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] mkcert is not installed!
    echo.
    echo Please install mkcert first:
    echo   Option 1: choco install mkcert
    echo   Option 2: Download from https://github.com/FiloSottile/mkcert/releases
    echo.
    pause
    exit /b 1
)

echo [1/4] Creating certs directory...
if not exist "certs" mkdir certs
cd certs

echo [2/4] Installing local Certificate Authority...
mkcert -install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install CA
    pause
    exit /b 1
)

echo [3/4] Generating SSL certificates for localhost...
mkcert localhost 127.0.0.1 ::1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to generate certificates
    pause
    exit /b 1
)

echo [4/4] Renaming certificate files...
ren localhost+2.pem cert.pem
ren localhost+2-key.pem key.pem

cd ..

echo.
echo ========================================
echo SUCCESS! SSL Certificates created!
echo ========================================
echo.
echo Certificate files:
echo   - certs/cert.pem
echo   - certs/key.pem
echo.
echo To start HTTPS server:
echo   python manage.py runsslserver --certificate certs/cert.pem --key certs/key.pem
echo.
echo Or simply:
echo   python manage.py runsslserver
echo.
pause
