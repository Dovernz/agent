$filePath = "D:\Thanh\Agent\GEMINI.md"
$sectionTitle = "## QUAT RULE 18 - PHAN MANH NGU CANH TU DONG"
$sectionContent = @"
$sectionTitle
- Khi Master Agent nhan yeu cau: BUOC BUOC goi hub shard auto <user_prompt> truoc bat ky hanh dong nao.
- Sau khi hoan thanh task du an: BUOC BUOC goi hub shard reset ve shard core (tiet kiem 89% token).
- CAM giu shard du an chuyen dung sang luot chat khac.
"@

if (-not (Test-Path $filePath)) {
    Write-Error "File khong ton tai: $filePath"
    exit 1
}

$content = Get-Content -Path $filePath -Raw -Encoding utf8

if (-not $content) {
    $content = ""
}

if ($content -notmatch [regex]::Escape($sectionTitle)) {
    if (-not $content.EndsWith("`n")) {
        $content += "`n"
    }
    $content += "`n" + $sectionContent.Trim() + "`n"
    [System.IO.File]::WriteAllText($filePath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "Da them thanh cong section vao $filePath"
} else {
    Write-Host "Section da ton tai trong file. Khong co thay doi nao duoc thuc hien."
}