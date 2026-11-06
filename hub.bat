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
if "%1"=="drift" goto drift
if "%1"=="notify" goto notify
if "%1"=="token-opt" goto token_opt
if "%1"=="gemini" goto gemini
if "%1"=="verify" goto verify

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

:drift
shift
uv run python "%SCRIPT_DIR%common\scripts\api_drift_detector.py" %*
exit /b %ERRORLEVEL%

:notify
shift
uv run python "%SCRIPT_DIR%common\scripts\notify_dispatcher.py" %*
exit /b %ERRORLEVEL%

:token_opt
shift
uv run python "%SCRIPT_DIR%common\scripts\token_optimizer.py" %*
exit /b %ERRORLEVEL%

:gemini
shift
uv run python "%SCRIPT_DIR%common\scripts\gemini_offloader.py" %*
exit /b %ERRORLEVEL%

:verify
shift
uv run python "%SCRIPT_DIR%common\scripts\output_verifier.py" %*
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
echo   hub drift           Kiem tra lech chuan API giua Backend Code va OpenAPI Spec
echo   hub notify          Ban thong bao su co & canh bao qua Telegram/Discord/Slack
echo   hub token-opt       Do luong, dinh vi diem nong va nen toi uu token su dung
echo   hub gemini          Chay tac vu nang qua Gemini API ngoai (0d) tiet kiem token
echo   hub verify [file]   Tham dinh chat luong, cu phap va an ninh output (.py, .json, .md)
echo   hub create          Khoi tao 1-click nhom agent cho du an moi tu template
echo   hub validate        Kiem tra tinh hop le 100%% cua toan bo 25 skills va 7 du an
echo =================================================================
exit /b 0
