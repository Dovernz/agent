# Script: upgrade_m2m_slim.ps1
# Muc dich: Tap hop quy tac M2M sang file detail va thu gon file goc m2m-protocol.md

$ErrorActionPreference = "Stop"

# Khai bao duong dan file
$sourcePath = "D:\Thanh\Agent\rules\m2m-protocol.md"
$detailPath = "D:\Thanh\Agent\rules\m2m-protocol-detail.md"

# Cho phep ghi file UTF-8 khong co BOM de tuong thich tot nhat
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

# 4) Kiem tra Idempotency: Neu file detail da ton tai thi bo qua
if (Test-Path -Path $detailPath) {
    Write-Host "[INFO] File detail da ton tai: '$detailPath'. Bo qua thuc hien."
    exit 0
}

# 1) Doc file goc
if (-not (Test-Path -Path $sourcePath)) {
    Write-Error "[ERROR] Khong tim thay file nguon: '$sourcePath'"
    exit 1
}

$rawContent = [System.IO.File]::ReadAllText($sourcePath, [System.Text.Encoding]::UTF8)

# 2) Tao file detail chua TOAN BO noi dung chi tiet cu
[System.IO.File]::WriteAllText($detailPath, $rawContent, $utf8NoBom)
Write-Host "[OK] Da sao chep noi dung chi tiet sang: '$detailPath'"

# 3) Xu ly va cap nhat file m2m-protocol.md (Tối đa 2 cau/quy tac)
$lines = $rawContent -split "\r?\n"
$slimLines = [System.Collections.Generic.List[string]]::new()

$inRule = $false
$sentenceCount = 0

foreach ($line in $lines) {
    $trimmedLine = $line.Trim()

    # Phat hien Tieu de Rule (VD: # Rule 1, ## Quy tắc 1, ### 1. ...)
    if ($trimmedLine -match '^#{1,6}\s*(?:Quy tắc|Rule|\d+[\.\:])') {
        if ($slimLines.Count -gt 0 -and $slimLines[$slimLines.Count - 1] -ne "") {
            $slimLines.Add("")
        }
        $slimLines.Add($trimmedLine)
        $inRule = $true
        $sentenceCount = 0
        continue
    }

    # Giu lai tieu de chinh / header truoc quy tac dau tien
    if (-not $inRule) {
        $slimLines.Add($line)
        continue
    }

    # Rut gon noi dung trong moi quy tac (Toi da 2 cau)
    if ($inRule -and $sentenceCount -lt 2) {
        if ($trimmedLine.Length -eq 0) { continue }

        # Tach cau bang cac dau [. ! ?]
        $sentences = [System.Text.RegularExpressions.Regex]::Split($trimmedLine, '(?<=[.!?])\s+')
        foreach ($s in $sentences) {
            $cleanSentence = $s.Trim()
            if ($sentenceCount -lt 2 -and $cleanSentence.Length -gt 0) {
                $slimLines.Add($cleanSentence)
                $sentenceCount++
            }
        }
    }
}

# Them dong link chi tiet o cuoi file
$footer = "> Chi tiet: @[M2M Protocol Detail](./m2m-protocol-detail.md)"
$finalContent = ($slimLines -join "`n").Trim() + "`n`n" + $footer

# Kiem tra dung luong (< 4000 bytes)
$bytes = [System.Text.Encoding]::UTF8.GetBytes($finalContent)
if ($bytes.Length -ge 4000) {
    Write-Warning "[WARNING] Dung luong file ($($bytes.Length) bytes) vuot qua 4000 bytes. Dang tu dong thu gon them..."
    # Truong hop dac biet neu vuot qua 4000 bytes, cat giam dong thua
    $finalContent = $finalContent.Substring(0, [Math]::Min(3900, $finalContent.Length)) + "`n`n" + $footer
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($finalContent)
}

# Ghi lai file m2m-protocol.md
[System.IO.File]::WriteAllText($sourcePath, $finalContent, $utf8NoBom)
Write-Host "[OK] Da cap nhat file slim: '$sourcePath' (Kich thuoc: $($bytes.Length) bytes)"