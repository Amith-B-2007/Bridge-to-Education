@echo off
REM ====================================================
REM RuralShiksha - One-Time Setup Script (Windows)
REM ====================================================
echo.
echo ============================================
echo  RuralShiksha - Setting up the project
echo ============================================
echo.

REM ---- Backend setup ----
echo [1/4] Installing Python dependencies...
cd backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install failed. Make sure Python 3.10+ is installed.
    pause
    exit /b 1
)

echo.
echo [2/4] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: migrations failed.
    pause
    exit /b 1
)

echo.
echo [3/4] Creating demo users...
python manage.py shell -c "from users.models import User, Student, Teacher; (not User.objects.filter(username='demo').exists() and (lambda: (u := User.objects.create_user(username='demo', email='demo@ruralsiksha.com', first_name='Demo', last_name='Student', password='demo123', role='student'), Student.objects.create(user=u, grade=5)))()); (not User.objects.filter(username='teacher').exists() and (lambda: (u := User.objects.create_user(username='teacher', email='teacher@ruralsiksha.com', first_name='Demo', last_name='Teacher', password='teacher123', role='teacher'), Teacher.objects.create(user=u, assigned_grades='5,6,7', assigned_subjects='Maths')))()); (not User.objects.filter(username='admin').exists() and User.objects.create_superuser('admin', 'admin@ruralsiksha.com', 'admin123', role='admin')); print('Demo users ready: demo/demo123, teacher/teacher123, admin/admin123')"

cd ..

REM ---- Frontend setup ----
echo.
echo [4/4] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: npm install failed. Make sure Node.js 18+ is installed.
    pause
    exit /b 1
)
cd ..

echo.
echo ============================================
echo  Setup complete!
echo ============================================
echo.
echo To start the project, run: start.bat
echo.
echo Demo logins:
echo   Student:  demo / demo123
echo   Teacher:  teacher / teacher123
echo   Admin:    admin / admin123
echo.
pause
