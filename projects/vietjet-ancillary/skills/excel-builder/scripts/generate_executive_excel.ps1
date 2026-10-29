<#
.SYNOPSIS
    Enterprise Executive Excel Report Generator for Antigravity Multi-Agent System.
.DESCRIPTION
    Generates publication-ready, multi-sheet Excel workbooks with:
    - Segoe UI typography hierarchy
    - Merged Title (14pt Bold, Dark Blue #1F4E78) & Subtitle (10pt Italic #595959)
    - 2-Tier Header System (Super-headers + Column Sub-headers with matching corporate palette)
    - Section Banner Rows (Light Grey #E6E6E6 with Dark Blue Bold text)
    - Formatted data cells with thin grey borders (#D9D9D9), center vertical alignment, and text wrapping
    - Color-coded status badges (Green = Complete/Matched, Blue = Filtered/Targeted, Red = Gap/Attention)
    - Pre-configured Freeze Panes and visible gridlines
.PARAMETER OutputPath
    The target file path of the .xlsx workbook.
.PARAMETER DataConfigPath
    Path to JSON configuration specifying sheets, headers, sections, and data rows.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$OutputPath,

    [Parameter(Mandatory=$false)]
    [string]$DataConfigPath
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Import-Module ImportExcel

# Ensure output directory exists
$outDir = [System.IO.Path]::GetDirectoryName($OutputPath)
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

# Check file lock
if (Test-Path $OutputPath) {
    try {
        $stream = [System.IO.File]::Open($OutputPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        $stream.Close()
    } catch {
        Write-Error "File is currently locked by another application. Please close it first: $OutputPath"
        exit 1
    }
}

Write-Host "Creating/Opening Excel Package: $OutputPath"
$excel = Open-ExcelPackage -Path $OutputPath -Create

function Build-ExecutiveSheet {
    param(
        [OfficeOpenXml.ExcelPackage]$Package,
        [string]$SheetName,
        [string]$Title,
        [string]$Subtitle,
        [array]$SuperHeaders,      # Array of @{ Range="A3:C3"; Text="Title"; Color=[Drawing.Color] }
        [array]$SubHeaders,        # Array of @{ Text="Col"; BgColor=[Drawing.Color]; Width=20; Align="Center" }
        [array]$Sections,          # Array of @{ Name="SEC 1"; Rows=@(...) }
        [int]$FreezeRow = 5,
        [int]$FreezeCol = 4
    )

    $existing = $Package.Workbook.Worksheets[$SheetName]
    if ($existing) {
        $Package.Workbook.Worksheets.Delete($existing)
    }

    $ws = $Package.Workbook.Worksheets.Add($SheetName)
    $ws.Cells.Style.Font.Name = "Segoe UI"
    $ws.Cells.Style.Font.Size = 10

    $totalCols = $SubHeaders.Count
    $lastColLetter = [char](64 + $totalCols)
    if ($totalCols -gt 26) {
        $firstLetter = [char](64 + [int]($totalCols / 26))
        $secondLetter = [char](64 + ($totalCols % 26))
        $lastColLetter = "$firstLetter$secondLetter"
    }

    # 1. Title Row
    $ws.Cells["A1:${lastColLetter}1"].Merge = $true
    $ws.Cells["A1"].Value = $Title
    $ws.Cells["A1"].Style.Font.Size = 14
    $ws.Cells["A1"].Style.Font.Bold = $true
    $ws.Cells["A1"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
    $ws.Cells["A1"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
    $ws.Cells["A1"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
    $ws.Cells["A1"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
    $ws.Cells["A1"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
    $ws.Row(1).Height = 35

    # 2. Subtitle Row
    $ws.Cells["A2:${lastColLetter}2"].Merge = $true
    $ws.Cells["A2"].Value = $Subtitle
    $ws.Cells["A2"].Style.Font.Size = 10
    $ws.Cells["A2"].Style.Font.Italic = $true
    $ws.Cells["A2"].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(89, 89, 89))
    $ws.Cells["A2"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
    $ws.Cells["A2"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(242, 242, 242))
    $ws.Cells["A2"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
    $ws.Cells["A2"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
    $ws.Row(2).Height = 22

    # 3. Super Headers (If present)
    if ($SuperHeaders -and $SuperHeaders.Count -gt 0) {
        foreach ($sh in $SuperHeaders) {
            $ws.Cells[$sh.Range].Merge = $true
            $ws.Cells[$sh.Range].Value = $sh.Text
            $ws.Cells[$sh.Range].Style.Font.Bold = $true
            $ws.Cells[$sh.Range].Style.Font.Size = 10
            $ws.Cells[$sh.Range].Style.Font.Color.SetColor([System.Drawing.Color]::White)
            $ws.Cells[$sh.Range].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
            $ws.Cells[$sh.Range].Style.Fill.BackgroundColor.SetColor($sh.Color)
            $ws.Cells[$sh.Range].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            $ws.Cells[$sh.Range].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
        }
        $ws.Row(3).Height = 25
        $headerRowStart = 4
    } else {
        $headerRowStart = 3
    }

    # 4. Sub Headers
    for ($c = 1; $c -le $totalCols; $c++) {
        $subH = $SubHeaders[$c - 1]
        $cell = $ws.Cells[$headerRowStart, $c]
        $cell.Value = $subH.Text
        $cell.Style.Font.Bold = $true
        $cell.Style.Font.Size = 9.5
        $cell.Style.WrapText = $true
        $cell.Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
        $cell.Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
        $cell.Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
        $cell.Style.Fill.BackgroundColor.SetColor($subH.BgColor)

        if ($subH.Width) {
            $ws.Column($c).Width = $subH.Width
        }
    }
    $ws.Row($headerRowStart).Height = 32

    # Borders for Header Rows
    $headerRows = if ($SuperHeaders -and $SuperHeaders.Count -gt 0) { @(3, 4) } else { @(3) }
    foreach ($hr in $headerRows) {
        for ($c = 1; $c -le $totalCols; $c++) {
            $ws.Cells[$hr, $c].Style.Border.Top.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Medium
            $ws.Cells[$hr, $c].Style.Border.Bottom.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Medium
            $ws.Cells[$hr, $c].Style.Border.Left.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
            $ws.Cells[$hr, $c].Style.Border.Right.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
        }
    }

    # 5. Populate Data Rows
    $currentRow = $headerRowStart + 1

    foreach ($sec in $Sections) {
        if ($sec.Name) {
            # Section Header Row
            $ws.Cells["A$currentRow:${lastColLetter}$currentRow"].Merge = $true
            $ws.Cells["A$currentRow"].Value = $sec.Name
            $ws.Cells["A$currentRow"].Style.Font.Bold = $true
            $ws.Cells["A$currentRow"].Style.Font.Size = 10.5
            $ws.Cells["A$currentRow"].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
            $ws.Cells["A$currentRow"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
            $ws.Cells["A$currentRow"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(230, 230, 230))
            $ws.Cells["A$currentRow"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
            $ws.Row($currentRow).Height = 22
            $currentRow++
        }

        foreach ($r in $sec.Rows) {
            for ($c = 1; $c -le $totalCols; $c++) {
                $val = $r[$c - 1]
                $cell = $ws.Cells[$currentRow, $c]
                $cell.Value = $val

                # Alignment
                $align = if ($SubHeaders[$c - 1].Align) { $SubHeaders[$c - 1].Align } else { "Left" }
                if ($align -eq "Center") {
                    $cell.Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
                } elseif ($align -eq "Right") {
                    $cell.Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Right
                } else {
                    $cell.Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Left
                }
                $cell.Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
                $cell.Style.WrapText = $true

                # Border
                $cell.Style.Border.Top.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Top.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Bottom.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Bottom.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Left.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Left.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Right.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Right.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))

                # Status Highlights
                if ($val -is [string]) {
                    if ($val -match "Đã chuyển đổi|In Both Tables|100% Khớp|Hoàn tất|Active") {
                        $cell.Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(55, 86, 35))
                        $cell.Style.Font.Bold = $true
                    } elseif ($val -match "Surcharge Only|SSR Only|Đã phân loại|Standard") {
                        $cell.Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
                    } elseif ($val -match "Data Gap|Lỗi|Cần lưu ý|Warning|Missing") {
                        $cell.Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(192, 0, 0))
                        $cell.Style.Font.Bold = $true
                    }
                }
            }
            $currentRow++
        }
    }

    # Freeze Panes & Gridlines
    $ws.View.FreezePanes($FreezeRow, $FreezeCol)
    $ws.View.ShowGridLines = $true
}

# If DataConfigPath provided, parse and build sheets
if ($DataConfigPath -and (Test-Path $DataConfigPath)) {
    $config = Get-Content -LiteralPath $DataConfigPath -Raw -Encoding utf8 | ConvertFrom-Json
    foreach ($sh in $config.Sheets) {
        Write-Host "Building Sheet: $($sh.Name)"
        
        $superList = @()
        if ($sh.SuperHeaders) {
            foreach ($s in $sh.SuperHeaders) {
                $c = [System.Drawing.ColorTranslator]::FromHtml($s.HexColor)
                $superList += @{ Range = $s.Range; Text = $s.Text; Color = $c }
            }
        }

        $subList = @()
        foreach ($sb in $sh.SubHeaders) {
            $c = [System.Drawing.ColorTranslator]::FromHtml($sb.HexBgColor)
            $subList += @{ Text = $sb.Text; BgColor = $c; Width = $sb.Width; Align = $sb.Align }
        }

        $secList = @()
        foreach ($sc in $sh.Sections) {
            $secList += @{ Name = $sc.Name; Rows = $sc.Rows }
        }

        Build-ExecutiveSheet -Package $excel `
            -SheetName $sh.Name `
            -Title $sh.Title `
            -Subtitle $sh.Subtitle `
            -SuperHeaders $superList `
            -SubHeaders $subList `
            -Sections $secList `
            -FreezeRow $sh.FreezeRow `
            -FreezeCol $sh.FreezeCol
    }
}

$excel.Save()
$excel.Dispose()
Write-Host "Workbook successfully generated and saved to: $OutputPath"
