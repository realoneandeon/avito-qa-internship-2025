@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запуск тестов API...
echo.
python -m pytest test_api.py -v --tb=short
pause

