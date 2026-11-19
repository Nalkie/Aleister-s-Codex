@echo off
rem Actualiza los datos y abre el pull request (doble clic). NO sube nada a Cloudflare: una persona revisa y fusiona el PR.
rem Para actualizar, publicar en Cloudflare y abrir el PR: actualizar.bat --pr.  Detalles: tools\publish.py y tools\pr.py.
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python tools\publish.py --quick --no-deploy --pr %*
set RC=%ERRORLEVEL%
echo.
if %RC%==0 (echo LISTO: datos actualizados y pull request abierto ^(la pagina en linea no cambia hasta que se publique^).) else if %RC%==3 (echo DATOS ACTUALIZADOS, pero el pull request fallo: mira el mensaje de arriba.) else (echo NO SE HIZO NADA: mira el error de arriba.)
echo.
pause
exit /b %RC%
