@echo off
cd /d "%~dp0"
call npm run build
if errorlevel 1 goto failed
start "" "http://127.0.0.1:4173"
node scripts/serve.mjs
goto end
:failed
echo The website could not be built. Check the error above.
pause
:end
