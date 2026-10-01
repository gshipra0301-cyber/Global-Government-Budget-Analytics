@echo off
cd /d "%~dp0"
py .\python_sql.py
if errorlevel 1 (
    echo.
    echo Script failed. Check the output above.
    pause
)
