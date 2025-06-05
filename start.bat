@echo off
echo Starting...
echo.

:: 启动后端
echo Starting backend...
cd backend
start cmd /k "call venv\Scripts\activate && python run.py"

:: 等待后端启动
timeout /t 3 /nobreak > nul

:: 启动前端
echo Starting frontend...
cd ..\frontend
start cmd /k "cd %CD% && npm run dev"

echo.
echo Done!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
pause