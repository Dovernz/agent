<#
.SYNOPSIS
    Super-fast, Zero-Token Data Profiler (Peek-and-Sample).
.DESCRIPTION
    Khảo sát cấu trúc file Excel (.xlsx) hoặc CSV (.csv) mà KHÔNG nạp toàn bộ dữ liệu vào bộ nhớ hay context LLM.
    Trả về:
    - Danh sách Sheets & Tọa độ bảng (Dimension, Total Rows, Total Cols).
    - Dòng Header (tên các cột).
    - Top N dòng mẫu (mặc định: 3 dòng).
    Giúp tiết kiệm 95-99% Token: Agent chỉ cần nhìn cấu trúc để viết script xử lý/tổng hợp.
.PARAMETER Path
    Đường dẫn tới file .xlsx hoặc .csv.
.PARAMETER MaxSampleRows
    Số dòng mẫu cần xem (mặc định: 3).
.PARAMETER MaxColumns
    Số cột tối đa hiển thị (mặc định: 15).
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,

    [int]$MaxSampleRows = 3,
    [int]$MaxColumns = 15
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Path)) {
    Write-Error "File not found: $Path"
    exit 1
}

$ext = [System.IO.Path]::GetExtension($Path).ToLower()

Write-Host "================================================================="
Write-Host "PEEK DATA PROFILE: $Path"
Write-Host "================================================================="

if ($ext -eq ".xlsx") {
    Import-Module ImportExcel -ErrorAction SilentlyContinue

    $pkg = Open-ExcelPackage -Path $Path
    $sheetCount = $pkg.Workbook.Worksheets.Count
    Write-Host "Total Worksheets: $sheetCount"

    foreach ($ws in $pkg.Workbook.Worksheets) {
        Write-Host "-----------------------------------------------------------------"
        Write-Host ("SHEET: [{0}] | Dimension: {1} | Total Rows: {2} | Total Cols: {3}" -f $ws.Name, $ws.Dimension.Address, $ws.Dimension.Rows, $ws.Dimension.Columns)
        
        if ($ws.Dimension.Rows -gt 0) {
            $numCols = [Math]::Min($MaxColumns, $ws.Dimension.Columns)
            
            # Header
            $headers = for ($c = 1; $c -le $numCols; $c++) { "" + $ws.Cells[1, $c].Value }
            Write-Host ("  Header (Cols 1-{0}): {1}" -f $numCols, ($headers -join " | "))
            
            # Sample rows
            $limitR = [Math]::Min(1 + $MaxSampleRows, $ws.Dimension.Rows)
            for ($r = 2; $r -le $limitR; $r++) {
                $vals = for ($c = 1; $c -le $numCols; $c++) { "" + $ws.Cells[$r, $c].Value }
                Write-Host ("  Sample Row {0}: {1}" -f $r, ($vals -join " | "))
            }
            if ($ws.Dimension.Rows -gt (1 + $MaxSampleRows)) {
                Write-Host ("  ... [{0} more rows omitted to save tokens]" -f ($ws.Dimension.Rows - 1 - $MaxSampleRows))
            }
        }
    }
    $pkg.Dispose()

} elseif ($ext -eq ".csv") {
    $lines = Get-Content -LiteralPath $Path -Head (1 + $MaxSampleRows)
    $totalLines = (Get-Content -LiteralPath $Path).Count
    Write-Host ("CSV File | Approx Total Lines: {0}" -f $totalLines)
    
    if ($lines.Count -gt 0) {
        Write-Host "  Header: $($lines[0])"
        for ($i = 1; $i -lt $lines.Count; $i++) {
            Write-Host ("  Sample Row {0}: {1}" -f $i, $lines[$i])
        }
        if ($totalLines -gt (1 + $MaxSampleRows)) {
            Write-Host ("  ... [{0} more rows omitted to save tokens]" -f ($totalLines - 1 - $MaxSampleRows))
        }
    }
} else {
    Write-Host "Unsupported file extension for peek: $ext"
}

Write-Host "================================================================="
Write-Host "NEXT STEP: Write a targeted PowerShell/Python script to process/filter data."
Write-Host "DO NOT print full table content into LLM context!"
Write-Host "================================================================="
