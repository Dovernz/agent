@echo off
setlocal enabledelayedexpansion

REM Antigravity Agent Hub Central CLI Launcher (hub.bat)
set SCRIPT_DIR=%~dp0

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="status" goto status
if "%1"=="doctor" goto doctor
if "%1"=="clean" goto clean
if "%1"=="lint" goto lint
if "%1"=="mock" goto mock
if "%1"=="db-profile" goto db_profile
if "%1"=="test" goto test
if "%1"=="changelog" goto changelog
if "%1"=="create" goto create
if "%1"=="validate" goto validate

echo [!] Lenh khong hop le: %1
echo Go 'hub help' de xem huong dan.
exit /b 1

:status
shift
uv run python "%SCRIPT_DIR%common\scripts\hub_status.py" %*
exit /b %ERRORLEVEL%

:doctor
shift
uv run python "%SCRIPT_DIR%common\scripts\hub_doctor.py" %*
exit /b %ERRORLEVEL%

:clean
shift
set TARGET=.
if not "%1"=="" (
    set TARGET=%1
    shift
)
uv run python "%SCRIPT_DIR%common\scripts\hub_cleaner.py" %TARGET% --clean %*
exit /b %ERRORLEVEL%

:lint
shift
uv run python "%SCRIPT_DIR%common\scripts\linter_guard.py" %*
exit /b %ERRORLEVEL%

:mock
shift
uv run python "%SCRIPT_DIR%common\scripts\mock_server_launcher.py" %*
exit /b %ERRORLEVEL%

:db_profile
shift
uv run python "%SCRIPT_DIR%common\scripts\db_query_profiler.py" %*
exit /b %ERRORLEVEL%

:test
shift
uv run python "%SCRIPT_DIR%common\scripts\test_matrix_runner.py" %*
exit /b %ERRORLEVEL%

:changelog
shift
uv run python "%SCRIPT_DIR%common\scripts\release_notes_builder.py" %*
exit /b %ERRORLEVEL%

:create
shift
uv run python "%SCRIPT_DIR%common\scripts\create_project.py" %*
exit /b %ERRORLEVEL%

:validate
shift
uv run python "%SCRIPT_DIR%common\scripts\validate_system.py" %*
exit /b %ERRORLEVEL%

:help
echo =================================================================
echo   ANTIGRAVITY MULTI-PROJECT AGENT HUB CLI (hub)
echo =================================================================
echo   Cac lenh tien ich nhanh:
echo.
echo   hub status          Xem bang dieu khien tien do Git va checkpoint cac du an
echo   hub doctor          Kiem tra toan dien Docker, ports, Git, token watchdog
echo   hub clean [path]    Don dep tap tin rac, script test va anh thua (Rule 11)
echo   hub lint [path]     Kiem tra cu phap Python/JSON va quet lo secret
echo   hub mock [spec]     Khoi chay Instant API Mock Server (CORS, CRUD, OpenAPI)
echo   hub db-profile [log] Phan tich truy van cham va mau truy van N+1
echo   hub test [path]     Chay da tang test matrix (Unit, Integration, Lint)
echo   hub changelog [repo] Tu dong tao Release Notes tu Git Conventional Commits
echo   hub create          Khoi tao 1-click nhom agent cho du an moi tu template
echo   hub validate        Kiem tra tinh hop le 100%% cua toan bo 25 skills va 7 du an
echo =================================================================
exit /b 0
