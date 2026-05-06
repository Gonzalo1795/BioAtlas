@echo off
title BioAtlas
cd /d C:\PROYECTOS\proyecto_atlas_v2

:: Cargar variables de entorno del fichero .env
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if not "%%a"=="" if not "%%b"=="" (
        set "%%a=%%b"
    )
)

:: Arrancar Stripe CLI en ventana minimizada
start "Stripe Webhook" /min "C:\Users\Gonza\AppData\Local\Microsoft\WinGet\Packages\Stripe.StripeCli_Microsoft.Winget.Source_8wekyb3d8bbwe\stripe.exe" listen --forward-to localhost:8000/premium/webhook/

:: Esperar 2 segundos a que Stripe arranque
timeout /t 2 /nobreak >nul

:: Arrancar Django
echo.
echo  BioAtlas arrancando en http://localhost:8000
echo.
python manage.py runserver

pause
