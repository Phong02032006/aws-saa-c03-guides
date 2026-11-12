@echo off
chcp 65001 >nul
title QuizCloud demo
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo [!] Chua cai Python. Tai tai https://www.python.org/downloads/ ^(nho tick "Add python.exe to PATH"^) roi chay lai.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Tao moi truong ao .venv ...
  %PY% -m venv .venv || goto :fail
)

echo [2/3] Cai thu vien (lan dau mat khoang 1 phut) ...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements-local.txt || goto :fail

cd web
if not exist "instance\quiz.db" (
  echo [3/3] Tao du lieu mau ...
  "..\.venv\Scripts\python.exe" -m flask --app app init-db --demo || goto :fail
)

echo.
echo  QuizCloud dang chay tai http://127.0.0.1:5000  (dong cua so nay de tat)
echo.
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:5000"
"..\.venv\Scripts\python.exe" -m flask --app app run --port 5000
goto :eof

:fail
echo.
echo [!] Co loi xay ra. Chup man hinh cua so nay gui cho nhom de ho tro.
pause
exit /b 1
