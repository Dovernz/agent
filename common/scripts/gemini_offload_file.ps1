[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$HubRoot,

    [Parameter(Mandatory = $true)]
    [string]$Prompt,

    [Parameter(Mandatory = $true)]
    [string]$OutFile,

    [Parameter(Mandatory = $false)]
    [string]$ContextFile,

    [Parameter(Mandatory = $false)]
    [ValidateSet('auto', 'bulk', 'standard', 'deep', 'ultra')]
    [string]$Tier = 'standard',

    [Parameter(Mandatory = $false)]
    [switch]$ReplaceExisting
)

$ErrorActionPreference = 'Stop'

$draftPath = $null

try {
    if ([string]::IsNullOrWhiteSpace($HubRoot)) {
        $HubRoot = $env:AGENT_HUB_ROOT
    }

    if ([string]::IsNullOrWhiteSpace($HubRoot)) {
        $scriptLocation = $PSScriptRoot
        if ([string]::IsNullOrWhiteSpace($scriptLocation)) {
            $scriptLocation = Split-Path -Parent $MyInvocation.MyCommand.Definition
        }
        $scriptItem = Get-Item -LiteralPath $scriptLocation
        $HubRoot = $scriptItem.Parent.Parent.FullName
    }

    $hubRoot = (Resolve-Path -LiteralPath $HubRoot).Path

    $offloaderPath = Join-Path $hubRoot "common\scripts\gemini_offloader.py"
    $verifierPath  = Join-Path $hubRoot "common\scripts\output_verifier.py"

    if (-not (Test-Path -LiteralPath $offloaderPath -PathType Leaf)) {
        Write-Error "Lỗi: Không tìm thấy file script gemini_offloader.py tại '$offloaderPath'."
        exit 1
    }

    if (-not (Test-Path -LiteralPath $verifierPath -PathType Leaf)) {
        Write-Error "Lỗi: Không tìm thấy file script output_verifier.py tại '$verifierPath'."
        exit 1
    }

    $workspace = $ExecutionContext.SessionState.Path.CurrentFileSystemLocation.ProviderPath

    function Resolve-WorkspacePath {
        param(
            [string]$Path,
            [string]$BaseDir
        )
        if ([System.IO.Path]::IsPathRooted($Path)) {
            return [System.IO.Path]::GetFullPath($Path)
        }
        return [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($BaseDir, $Path))
    }

    $resolvedOutFile = Resolve-WorkspacePath -Path $OutFile -BaseDir $workspace

    if ((Test-Path -LiteralPath $resolvedOutFile) -and (-not $ReplaceExisting)) {
        Write-Error "Lỗi: File đích '$resolvedOutFile' đã tồn tại. Sử dụng tham số -ReplaceExisting để cho phép ghi đè."
        exit 1
    }

    $resolvedContextFile = $null
    if (-not [string]::IsNullOrWhiteSpace($ContextFile)) {
        $resolvedContextFile = Resolve-WorkspacePath -Path $ContextFile -BaseDir $workspace
        if (-not (Test-Path -LiteralPath $resolvedContextFile -PathType Leaf)) {
            Write-Error "Lỗi: File ngữ cảnh '$resolvedContextFile' không tồn tại."
            exit 1
        }

        $ctxLeaf = Split-Path -Leaf $resolvedContextFile
        $ctxExt  = [System.IO.Path]::GetExtension($resolvedContextFile).ToLowerInvariant()

        $isSensitiveName = ($ctxLeaf -match '^(?i)\.env(?:$|\.)') -or
                           ($ctxLeaf -match '(?i)(credentials|secrets)') -or
                           ($ctxLeaf -match '(?i)(id_rsa|id_ed25519|id_dsa|id_ecdsa|private[_-]?key)')

        $isSensitiveExt  = $ctxExt -in @('.pem', '.key', '.pkcs12', '.pfx', '.asc', '.kdbx')

        if ($isSensitiveName -or $isSensitiveExt) {
            Write-Error "Lỗi bảo mật: File ngữ cảnh '$ctxLeaf' bị từ chối vì chứa thông tin nhạy cảm hoặc khóa bảo mật."
            exit 1
        }
    }

    $cmdUv     = Get-Command uv -ErrorAction SilentlyContinue
    $cmdPython = Get-Command python -ErrorAction SilentlyContinue

    $exeLauncher = $null
    $baseArgs    = @()

    if ($cmdUv) {
        $exeLauncher = $cmdUv.Source
        $baseArgs    = @('run', '--directory', $hubRoot, '--no-project', 'python')
    } elseif ($cmdPython) {
        $exeLauncher = $cmdPython.Source
        $baseArgs    = @()
    } else {
        Write-Error "Lỗi: Không tìm thấy 'uv' hoặc 'python' trong môi trường PATH."
        exit 1
    }

    $outExt     = [System.IO.Path]::GetExtension($resolvedOutFile)
    $tempFolder = [System.IO.Path]::GetTempPath()
    $draftPath  = Join-Path $tempFolder ("gemini_draft_" + [System.Guid]::NewGuid().ToString("N") + $outExt)

    $offloaderArgs = $baseArgs + @($offloaderPath, '--prompt', $Prompt, '--out', $draftPath, '--tier', $Tier, '--no-cache')
    if ($resolvedContextFile) {
        $offloaderArgs += @('--file', $resolvedContextFile)
    }

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $null = & $exeLauncher @offloaderArgs 2>&1
        $offloaderExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($offloaderExitCode -ne 0) {
        Write-Error "Lỗi: Quá trình tạo mã qua gemini_offloader thất bại (Mã lỗi: $offloaderExitCode)."
        exit 1
    }

    if (-not (Test-Path -LiteralPath $draftPath -PathType Leaf) -or ((Get-Item -LiteralPath $draftPath).Length -eq 0)) {
        Write-Error "Lỗi: File nháp không được khởi tạo hoặc có kích thước bằng 0."
        exit 1
    }

    $verifierArgs = $baseArgs + @($verifierPath, '--json', $draftPath)
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $verifierOutput = & $exeLauncher @verifierArgs 2>&1
        $verifierExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($verifierExitCode -ne 0) {
        Write-Error "Lỗi: Quá trình xác minh file nháp qua output_verifier thất bại (Mã lỗi: $verifierExitCode)."
        exit 1
    }

    $rawJson = ($verifierOutput | Out-String)
    $vData = $null
    try {
        $vData = $rawJson | ConvertFrom-Json
    } catch {
        Write-Error "Lỗi: Không thể phân tích dữ liệu JSON phản hồi từ output_verifier."
        exit 1
    }

    $passed = [bool]$vData.passed
    $score  = [int]$vData.score

    if (-not $passed -or $score -lt 70) {
        Write-Error ("Validation failed (passed={0}, score={1}/100)." -f $passed, $score)
        exit 1
    }

    if ($outExt -eq '.ps1' -or $outExt -eq '.psm1') {
        $tokens = $null
        $errors = $null
        $null = [System.Management.Automation.Language.Parser]::ParseFile($draftPath, [ref]$tokens, [ref]$errors)
        if ($errors -and $errors.Count -gt 0) {
            $errMessages = ($errors | ForEach-Object { $_.Message }) -join "; "
            Write-Error ("PowerShell syntax error: {0}" -f $errMessages)
            exit 1
        }
    }

    $parentDir = Split-Path -Parent $resolvedOutFile
    if (-not (Test-Path -LiteralPath $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    if (Test-Path -LiteralPath $resolvedOutFile) {
        if ($ReplaceExisting) {
            $timestamp = Get-Date -Format "yyyyMMddHHmmss"
            $backupPath = "$resolvedOutFile.bak_$timestamp"
            Copy-Item -LiteralPath $resolvedOutFile -Destination $backupPath -Force
        } else {
            Write-Error "Lỗi: File đích '$resolvedOutFile' đã tồn tại."
            exit 1
        }
    }

    Copy-Item -LiteralPath $draftPath -Destination $resolvedOutFile -Force

    Write-Host "Tạo file thành công!" -ForegroundColor Green
    Write-Host "Đường dẫn đầu ra: $resolvedOutFile"
    Write-Host ('Điểm xác minh tĩnh: {0}/100' -f $score)
    Write-Host "Lưu ý: Chưa chạy các bài kiểm thử dự án (project tests)."
}
finally {
    if ($draftPath -and (Test-Path -LiteralPath $draftPath)) {
        Remove-Item -LiteralPath $draftPath -Force -ErrorAction SilentlyContinue
    }
}