# Script: upgrade_master_agent.ps1
# Mo ta: Refactor SKILL.md, tach Section 3, 4, 5 sang references/m2m-dispatch.md va cap nhat lien ket.

$ErrorActionPreference = "Stop"

# 1. Khai bao duong dan
$baseDir   = "D:\Thành\Agent\common\skills\master-agent"
$refDir    = Join-Path $baseDir "references"
$skillPath = Join-Path $baseDir "SKILL.md"
$m2mPath   = Join-Path $refDir "m2m-dispatch.md"
$refLine   = "> Chi tiet M2M: @[M2M Dispatch Protocol](./references/m2m-dispatch.md)"

# Thiet lap UTF-8 Encoding khong co BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

# 2. Tao thu muc references neu chua co
if (-not (Test-Path -Path $refDir)) {
    New-Item -Path $refDir -ItemType Directory -Force | Out-Null
}

# Kiem tra xem file SKILL.md co ton tai hay khong
if (-not (Test-Path -Path $skillPath)) {
    Write-Error "Khong tim thay file: $skillPath"
    exit 1
}

# Doc noi dung SKILL.md
$skillContent = [System.IO.File]::ReadAllText($skillPath, [System.Text.Encoding]::UTF8)

# 3. Tach Section 3, 4, 5 neu chua duoc tach (Dam bao tinh Idempotent)
# Pattern tim bat dau tu Section 3 (Giao Thuc Giao Viec M2M JSON)
$sec3Pattern = '(?m)^#{1,4}\s*(?:Section\s*3|3[\.\:\s]).*?Giao\s*Th[uú]c\s*Giao\s*Vi[eê]c\s*M2M'
$match = [regex]::Match($skillContent, $sec3Pattern)

if ($match.Success) {
    $sec3Index = $match.Index
    $part1 = $skillContent.Substring(0, $sec3Index).TrimEnd()
    $part2 = $skillContent.Substring($sec3Index).Trim()

    # Loai bo dong reference neu da co trong part2
    $part2 = ($part2 -replace '(?m)^\>\s*Chi tiet M2M:.*$', '').Trim()

    # Ghi file references/m2m-dispatch.md với UTF-8
    [System.IO.File]::WriteAllText($m2mPath, $part2, $utf8NoBom)

    # Cap nhat noi dung SKILL.md (Frontmatter + Section 1 + Section 2 + Reference Line)
    $newSkillContent = $part1 + "`n`n" + $refLine + "`n"
    [System.IO.File]::WriteAllText($skillPath, $newSkillContent, $utf8NoBom)
} else {
    # Neu da tach roi, kiem tra va cap nhat dong reference neu chua co
    if ($skillContent -notmatch [regex]::Escape($refLine)) {
        $part1 = ($skillContent -replace '(?m)^\>\s*Chi tiet M2M:.*$', '').TrimEnd()
        $newSkillContent = $part1 + "`n`n" + $refLine + "`n"
        [System.IO.File]::WriteAllText($skillPath, $newSkillContent, $utf8NoBom)
    }
}

# 4. Kiem tra va xac minh cac tu khoa bat buoc trong SKILL.md
$updatedSkillContent = [System.IO.File]::ReadAllText($skillPath, [System.Text.Encoding]::UTF8)
$requiredKeywords = @('dental', 'airflow', 'ancillary', 'brd', 'pc-builder', 'supervisor', 'master-agent', '/master-agent')

foreach ($kw in $requiredKeywords) {
    if ($updatedSkillContent -notmatch [regex]::Escape($kw)) {
        Write-Error "Kiem tra thieu tu khoa: Tu khoa '$kw' khong tim thay trong $skillPath"
        exit 1
    }
}

Write-Host "Upgrade master-agent thanh cong va dam bao tinh Idempotent."