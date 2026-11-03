@echo off
rem Actualiza los datos de la pagina y los publica en Cloudflare (doble clic). Ver tools\publish.py.
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python tools\publish.py %*
set RC=%ERRORLEVEL%
echo.
if %RC%==0 (echo LISTO: la pagina se actualizo.) else if %RC%==2 (echo PUBLICADO, pero la pagina en linea todavia no muestra la fecha de hoy: recarga sin cache en un minuto.) else if %RC%==3 (echo PUBLICADO y verificado, pero el pull request fallo: mira el mensaje de arriba.) else (echo NO SE PUBLICO NADA: mira el error de arriba.)
echo.
pause
exit /b %RC%
