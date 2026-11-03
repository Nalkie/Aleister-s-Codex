@echo off
rem Igual que actualizar.bat pero sin las listas de imagenes de TCGplayer (la descarga mas lenta).
call "%~dp0actualizar.bat" --quick %*
