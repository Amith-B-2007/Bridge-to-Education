@echo off
REM ====================================================
REM RuralShiksha - Start Both Servers (Windows)
REM ====================================================
echo.
echo ============================================
echo  Starting RuralShiksha
echo ============================================
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo.
echo  Demo logins:
echo    Student:  demo / demo123
echo    Teacher:  teacher / teacher123
echo    Admin:    admin / admin123
echo.
echo ============================================
echo.

REM Start backend in a new window
start "RuralShiksha Backend" cmd /k "cd backend && python manage.py runserver 0.0.0.0:8000"

REM Wait for backend to come up
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "RuralShiksha Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting in separate windows.
echo Open your browser at http://localhost:5173
echo.
echo Press any key to exit this launcher (servers will keep running)...
pause >nul
