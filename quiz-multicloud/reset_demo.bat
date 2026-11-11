@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist "web\instance" rmdir /s /q "web\instance"
echo Da xoa du lieu demo. Chay lai run_demo.bat de tao du lieu mau moi.
pause
