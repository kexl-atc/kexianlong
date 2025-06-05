@echo off
echo Starting...
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please install Python 3.6+
    pause
    exit /b 1
)

:: 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found, please install Node.js 14+
    pause
    exit /b 1
)

:: 安装后端
echo Installing backend dependencies...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
echo Please edit backend\.env file to configure the key
echo.

:: 安装前端
echo Installing frontend dependencies...
cd ..\frontend
call npm install
echo.

echo Done!
echo Please edit backend\.env file to configure the key
echo Then run start.bat to start the system
pause