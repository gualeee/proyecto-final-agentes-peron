@echo off
title Servidor Agente de Tickets - UCEMA Trabajo Final
cd /d "%~dp0"

echo ========================================================
echo   Iniciando Servidor del Agente de Tickets (HubSpot + Gemini)
echo ========================================================
echo.
echo Abriendo dashboard en el navegador: http://localhost:8000
echo Para detener el servidor presiona Ctrl + C en esta ventana.
echo.

start http://localhost:8000
python app/server.py

pause
