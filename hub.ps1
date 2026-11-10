<#

.SYNOPSIS

    Antigravity Agent Hub Central CLI Launcher (hub.ps1)

.DESCRIPTION

    Quick-access launcher for all common hub operations, health checks,

    linting, testing, and mock servers.

#>



param(

    [Parameter(Position=0)]

    [string]$Command = "help",



    [Parameter(ValueFromRemainingArguments=$true)]

    [string[]]$RemainingArgs

)



$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path



switch ($Command.ToLower()) {

    "status" {

        uv run python "$ScriptDir\common\scripts\hub_status.py" @RemainingArgs

    }

    "doctor" {

        uv run python "$ScriptDir\common\scripts\hub_doctor.py" @RemainingArgs

    }

    "clean" {

        $target = if ($RemainingArgs.Count -gt 0) { $RemainingArgs[0] } else { "." }

        $rest = if ($RemainingArgs.Count -gt 1) { $RemainingArgs[1..($RemainingArgs.Count - 1)] } else { @() }

        uv run python "$ScriptDir\common\scripts\hub_cleaner.py" $target --clean @rest

    }

    "lint" {

        uv run python "$ScriptDir\common\scripts\linter_guard.py" @RemainingArgs

    }

    "mock" {

        uv run python "$ScriptDir\common\scripts\mock_server_launcher.py" @RemainingArgs

    }

    "db-profile" {

        uv run python "$ScriptDir\common\scripts\db_query_profiler.py" @RemainingArgs

    }

    "test" {

        uv run python "$ScriptDir\common\scripts\test_matrix_runner.py" @RemainingArgs

    }

    "changelog" {

        uv run python "$ScriptDir\common\scripts\release_notes_builder.py" @RemainingArgs

    }

    "create" {

        uv run python "$ScriptDir\common\scripts\create_project.py" @RemainingArgs

    }

    "validate" {

        uv run python "$ScriptDir\common\scripts\validate_system.py" @RemainingArgs

    }

    "drift" {

        uv run python "$ScriptDir\common\scripts\api_drift_detector.py" @RemainingArgs

    }

    "notify" {

        uv run python "$ScriptDir\common\scripts\notify_dispatcher.py" @RemainingArgs

    }

    "token-opt" {

        uv run python "$ScriptDir\common\scripts\token_optimizer.py" --hub "$ScriptDir" @RemainingArgs

    }

    "gemini" {

        uv run python "$ScriptDir\common\scripts\gemini_offloader.py" @RemainingArgs

    }

    "usage" {

        uv run python "$ScriptDir\common\scripts\gemini_offloader.py" --pool-status @RemainingArgs

    }

    "verify" {

        uv run python "$ScriptDir\common\scripts\output_verifier.py" @RemainingArgs

    }

    "smoke" {

        uv run python "$ScriptDir\common\scripts\smoke_test_runner.py" @RemainingArgs

    }

    "fanout" {

        uv run python "$ScriptDir\common\scripts\task_fanout_planner.py" @RemainingArgs

    }

    "shard" {

        uv run python "$ScriptDir\common\scripts\context_sharder.py" --hub "$ScriptDir" @RemainingArgs

    }

    "sync" {

        # Đồng bộ GEMINI.md master vào tất cả workspace của các project Antigravity

        uv run python "$ScriptDir\common\scripts\sync_rules.py" @RemainingArgs

    }

    "package" {
        uv run python "$ScriptDir\common\scripts\package_web_app.py" @RemainingArgs
    }

    default {

        Write-Host "=================================================================" -ForegroundColor Cyan

        Write-Host "  ANTIGRAVITY MULTI-PROJECT AGENT HUB CLI (hub.ps1)" -ForegroundColor Yellow

        Write-Host "=================================================================" -ForegroundColor Cyan

        Write-Host "  Các lệnh tiện ích nhanh:`n"

        Write-Host "  .\hub.ps1 status          Xem bảng điều khiển tiến độ Git và checkpoint các dự án" -ForegroundColor Green

        Write-Host "  .\hub.ps1 doctor          Kiểm tra toàn diện Docker, ports, Git, token watchdog" -ForegroundColor Green

        Write-Host "  .\hub.ps1 smoke           Kiểm tra tức thì (0.5s) HTTP/TCP endpoints các dịch vụ và containers" -ForegroundColor Green

        Write-Host "  .\hub.ps1 clean [path]    Dọn dẹp tập tin rác, script test và ảnh thừa (Rule 11)" -ForegroundColor Green

        Write-Host "  .\hub.ps1 lint [path]     Kiểm tra cú pháp Python/JSON và quét lộ secret" -ForegroundColor Green

        Write-Host "  .\hub.ps1 mock [spec]     Khởi chạy Instant API Mock Server (CORS, CRUD, OpenAPI)" -ForegroundColor Green

        Write-Host "  .\hub.ps1 db-profile      Phân tích truy vấn chậm và mẫu truy vấn N+1" -ForegroundColor Green

        Write-Host "  .\hub.ps1 test [path]     Chạy đa tầng test matrix (Unit, Integration, Lint)" -ForegroundColor Green

        Write-Host "  .\hub.ps1 changelog       Tự động tạo Release Notes từ Git Conventional Commits" -ForegroundColor Green

        Write-Host "  .\hub.ps1 drift           Kiểm tra lệch chuẩn API giữa Backend Code và OpenAPI Spec" -ForegroundColor Green

        Write-Host "  .\hub.ps1 notify          Bắn thông báo sự cố & cảnh báo qua Telegram/Discord/Slack" -ForegroundColor Green

        Write-Host "  .\hub.ps1 token-opt       Đo lường, định vị điểm nóng và nén tối ưu token sử dụng" -ForegroundColor Green

        Write-Host "  .\hub.ps1 shard [args]    Phân mảnh context động theo từng dự án, giảm 90% token System Prompt" -ForegroundColor Green

        Write-Host "  .\hub.ps1 gemini          Chạy tác vụ nặng qua Gemini API ngoài (0đ) để tiết kiệm token" -ForegroundColor Green

        Write-Host "  .\hub.ps1 usage           Bảng điều khiển & thống kê hạn mức 7 key và từng model" -ForegroundColor Green

        Write-Host "  .\hub.ps1 verify [file]   Thẩm định chất lượng, cú pháp & an ninh output (.py, .json, .md)" -ForegroundColor Green

        Write-Host "  .\hub.ps1 fanout [args]   Lập kế hoạch phân rã N sub-agent & tầng API theo độ phức tạp" -ForegroundColor Green

        Write-Host "  .\hub.ps1 create          Khởi tạo 1-click nhóm agent cho dự án mới từ template" -ForegroundColor Green

        Write-Host "  .\hub.ps1 validate        Kiểm tra tính hợp lệ 100% của toàn bộ 25 skills và 7 dự án" -ForegroundColor Green

        Write-Host "  .\hub.ps1 sync [--force]  Đồng bộ GEMINI.md rules vào tất cả workspace của các dự án" -ForegroundColor Green
        Write-Host "  .\hub.ps1 package [args]   Đóng gói web 1-click standalone cho user test kèm lock key" -ForegroundColor Green

        Write-Host "=================================================================" -ForegroundColor Cyan

    }

}

