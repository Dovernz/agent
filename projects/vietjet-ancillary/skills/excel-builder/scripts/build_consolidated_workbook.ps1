<#
.SYNOPSIS
    Tự động xây dựng workbook Excel 3 sheets đối chiếu Ancillary chuẩn Ban Tổng Giám đốc.
.DESCRIPTION
    Đọc dữ liệu từ:
    - Ancillary_Product_Groups_VN.csv (hoặc csv mapping)
    - Ancillary Type.xlsx (bảng cũ 110 dòng, lọc bỏ 10 mã thuế phí sân bay/vé: AI, SG, OO, OP, AS, APPS, BKK E8, SF, MO, FA)
    - Định nghĩa 5 views Databricks Medallion
    Sinh file: D:\Vietjet\2026\Tờ trình\Ancillary_Product_Groups_VN.xlsx
#>

param(
    [string]$TargetFolder = "D:\Vietjet\2026\Tờ trình",
    [string]$OutputFileName = "Ancillary_Product_Groups_VN.xlsx"
)

$ErrorActionPreference = 'Stop'
Import-Module ImportExcel
Add-Type -AssemblyName System.Drawing

$excelPath = Join-Path $TargetFolder $OutputFileName
$csvPath = Join-Path $TargetFolder "Ancillary_Product_Groups_VN.csv"
$legacyExcelPath = Join-Path $TargetFolder "Ancillary Type.xlsx"

Write-Host "Target Excel: $excelPath"

# Kiểm tra file lock
if (Test-Path $excelPath) {
    try {
        $stream = [System.IO.File]::Open($excelPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        $stream.Close()
    } catch {
        Write-Error "File is currently locked by another application. Please close it first: $excelPath"
        exit 1
    }
}

$excel = Open-ExcelPackage -Path $excelPath -Create

# ------------------------------------------------------------------------------
# SHEET 1: Ancillary_Product_Groups (Bảng mới PSS Surcharge & SSR)
# ------------------------------------------------------------------------------
$ws1Name = "Ancillary_Product_Groups"
$existingWs1 = $excel.Workbook.Worksheets[$ws1Name]
if ($existingWs1) { $excel.Workbook.Worksheets.Delete($existingWs1) }

$ws1 = $excel.Workbook.Worksheets.Add($ws1Name)
$ws1.Cells.Style.Font.Name = "Segoe UI"
$ws1.Cells.Style.Font.Size = 10

# Title Row 1
$ws1.Cells["A1:L1"].Merge = $true
$ws1.Cells["A1"].Value = "BẢNG PHÂN LOẠI NHÓM SẢN PHẨM ANCILLARY & LOGIC ÁNH XẠ (SURCHARGE & SSR)"
$ws1.Cells["A1"].Style.Font.Size = 14
$ws1.Cells["A1"].Style.Font.Bold = $true
$ws1.Cells["A1"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws1.Cells["A1"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws1.Cells["A1"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
$ws1.Cells["A1"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
$ws1.Cells["A1"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
$ws1.Row(1).Height = 35

# Subtitle Row 2
$ws1.Cells["A2:L2"].Merge = $true
$ws1.Cells["A2"].Value = "Phân loại chi tiết, quy tắc nhận diện trên hệ thống PSS Surcharge & SSR, tình trạng và phạm vi áp dụng (Dùng cho Tờ trình & Báo cáo)"
$ws1.Cells["A2"].Style.Font.Size = 10
$ws1.Cells["A2"].Style.Font.Italic = $true
$ws1.Cells["A2"].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(89, 89, 89))
$ws1.Cells["A2"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws1.Cells["A2"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(242, 242, 242))
$ws1.Cells["A2"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
$ws1.Cells["A2"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
$ws1.Row(2).Height = 22

# Super Headers Row 3
$ws1.Cells["A3:C3"].Merge = $true
$ws1.Cells["A3"].Value = "THÔNG TIN SẢN PHẨM CHUNG"
$ws1.Cells["A3"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws1.Cells["A3"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(47, 84, 150))
$ws1.Cells["A3"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws1.Cells["A3"].Style.Font.Bold = $true
$ws1.Cells["A3"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center

$ws1.Cells["D3:G3"].Merge = $true
$ws1.Cells["D3"].Value = "BẢNG ĐỊNH NGHĨA SURCHARGE (PSS Surcharge)"
$ws1.Cells["D3"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws1.Cells["D3"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(192, 0, 0))
$ws1.Cells["D3"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws1.Cells["D3"].Style.Font.Bold = $true
$ws1.Cells["D3"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center

$ws1.Cells["H3:J3"].Merge = $true
$ws1.Cells["H3"].Value = "BẢNG ĐỊNH NGHĨA SSR (PSS SSR)"
$ws1.Cells["H3"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws1.Cells["H3"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(55, 86, 35))
$ws1.Cells["H3"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws1.Cells["H3"].Style.Font.Bold = $true
$ws1.Cells["H3"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center

$ws1.Cells["K3:L3"].Merge = $true
$ws1.Cells["K3"].Value = "TRẠNG THÁI & GHI CHÚ PHẠM VI"
$ws1.Cells["K3"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws1.Cells["K3"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(112, 48, 160))
$ws1.Cells["K3"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws1.Cells["K3"].Style.Font.Bold = $true
$ws1.Cells["K3"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
$ws1.Row(3).Height = 25

# Sub Headers Row 4
$headers1 = @(
    "STT (No)",
    "Nhóm sản phẩm`n(Product Group)",
    "Loại sản phẩm Ancillary`n(Ancillary Product Type)",
    "Charge Type Desc",
    "Charge Type Ident",
    "Ví dụ Surcharge Ident",
    "Logic & Pattern nhận diện Surcharge",
    "SSR Category Name",
    "Ví dụ SSR Name",
    "Logic & Pattern nhận diện SSR",
    "Trạng thái hệ thống`n(System Status)",
    "Ghi chú phạm vi & Đường bay (Tiếng Việt)"
)

for ($c = 1; $c -le 12; $c++) {
    $cell = $ws1.Cells[4, $c]
    $cell.Value = $headers1[$c - 1]
    $cell.Style.Font.Bold = $true
    $cell.Style.Font.Size = 9.5
    $cell.Style.WrapText = $true
    $cell.Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
    $cell.Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
    $cell.Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
    
    if ($c -le 3) { $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(217, 225, 242)) }
    elseif ($c -le 7) { $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(252, 228, 214)) }
    elseif ($c -le 10) { $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(226, 239, 218)) }
    else { $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(225, 213, 231)) }
}
$ws1.Row(4).Height = 32

if (Test-Path $csvPath) {
    $csvFull = Import-Csv -LiteralPath $csvPath -Header "c1","c2","c3","c4","c5","c6","c7","c8","c9","c10","c11","c12"
    $dataRows = $csvFull | Select-Object -Skip 4
    $currentRow = 5

    foreach ($row in $dataRows) {
        if ($row.c1 -match '^SECTION') {
            $ws1.Cells["A$currentRow:L$currentRow"].Merge = $true
            $ws1.Cells["A$currentRow"].Value = $row.c1
            $ws1.Cells["A$currentRow"].Style.Font.Bold = $true
            $ws1.Cells["A$currentRow"].Style.Font.Size = 10.5
            $ws1.Cells["A$currentRow"].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
            $ws1.Cells["A$currentRow"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
            $ws1.Cells["A$currentRow"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(230, 230, 230))
            $ws1.Cells["A$currentRow"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
            $ws1.Row($currentRow).Height = 22
        } elseif ($row.c1 -match '^\d+$') {
            $ws1.Cells[$currentRow, 1].Value = [int]$row.c1
            $ws1.Cells[$currentRow, 1].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            $ws1.Cells[$currentRow, 2].Value = $row.c2
            $ws1.Cells[$currentRow, 3].Value = $row.c3
            $ws1.Cells[$currentRow, 4].Value = $row.c4
            $ws1.Cells[$currentRow, 5].Value = $row.c5
            $ws1.Cells[$currentRow, 5].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            $ws1.Cells[$currentRow, 6].Value = $row.c6
            $ws1.Cells[$currentRow, 7].Value = $row.c7
            $ws1.Cells[$currentRow, 8].Value = $row.c8
            $ws1.Cells[$currentRow, 9].Value = $row.c9
            $ws1.Cells[$currentRow, 10].Value = $row.c10
            $ws1.Cells[$currentRow, 11].Value = $row.c11
            $ws1.Cells[$currentRow, 11].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            
            if ($row.c11 -eq "In Both Tables") {
                $ws1.Cells[$currentRow, 11].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(55, 86, 35))
                $ws1.Cells[$currentRow, 11].Style.Font.Bold = $true
            } elseif ($row.c11 -like "*Only") {
                $ws1.Cells[$currentRow, 11].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
            } elseif ($row.c11 -like "*Gap*") {
                $ws1.Cells[$currentRow, 11].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(192, 0, 0))
                $ws1.Cells[$currentRow, 11].Style.Font.Bold = $true
            }
            
            $ws1.Cells[$currentRow, 12].Value = $row.c12
            
            for ($c = 1; $c -le 12; $c++) {
                $cell = $ws1.Cells[$currentRow, $c]
                $cell.Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
                $cell.Style.WrapText = $true
                $cell.Style.Border.Top.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Top.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Bottom.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Bottom.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Left.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Left.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Right.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Right.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
            }
        }
        $currentRow++
    }
}

for ($r = 3; $r -le 4; $r++) {
    for ($c = 1; $c -le 12; $c++) {
        $ws1.Cells[$r, $c].Style.Border.Top.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Medium
        $ws1.Cells[$r, $c].Style.Border.Bottom.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Medium
        $ws1.Cells[$r, $c].Style.Border.Left.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
        $ws1.Cells[$r, $c].Style.Border.Right.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
    }
}

$ws1.Column(1).Width = 7
$ws1.Column(2).Width = 18
$ws1.Column(3).Width = 26
$ws1.Column(4).Width = 18
$ws1.Column(5).Width = 12
$ws1.Column(6).Width = 25
$ws1.Column(7).Width = 32
$ws1.Column(8).Width = 20
$ws1.Column(9).Width = 25
$ws1.Column(10).Width = 32
$ws1.Column(11).Width = 15
$ws1.Column(12).Width = 42

$ws1.View.FreezePanes(5, 4)
$ws1.View.ShowGridLines = $true

# ------------------------------------------------------------------------------
# SHEET 2: Legacy_Ancillary_Products (Bảng cũ 100 sản phẩm đã lọc)
# ------------------------------------------------------------------------------
$ws2Name = "Legacy_Ancillary_Products"
$existingWs2 = $excel.Workbook.Worksheets[$ws2Name]
if ($existingWs2) { $excel.Workbook.Worksheets.Delete($existingWs2) }

$ws2 = $excel.Workbook.Worksheets.Add($ws2Name)
$ws2.Cells.Style.Font.Name = "Segoe UI"
$ws2.Cells.Style.Font.Size = 10

# Title Row 1
$ws2.Cells["A1:L1"].Merge = $true
$ws2.Cells["A1"].Value = "BẢNG ĐỐI CHIẾU SẢN PHẨM ANCILLARY HỆ THỐNG CŨ (LEGACY ANCILLARY MAPPING)"
$ws2.Cells["A1"].Style.Font.Size = 14
$ws2.Cells["A1"].Style.Font.Bold = $true
$ws2.Cells["A1"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws2.Cells["A1"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws2.Cells["A1"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
$ws2.Cells["A1"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
$ws2.Cells["A1"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
$ws2.Row(1).Height = 35

# Subtitle Row 2
$ws2.Cells["A2:L2"].Merge = $true
$ws2.Cells["A2"].Value = "Quy hoạch 100 mã danh mục Ancillary bảng cũ (loại bỏ thuế phí sân bay & giá vé) sang 9 nhóm chuẩn và logic Databricks Medallion"
$ws2.Cells["A2"].Style.Font.Size = 10
$ws2.Cells["A2"].Style.Font.Italic = $true
$ws2.Cells["A2"].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(89, 89, 89))
$ws2.Cells["A2"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws2.Cells["A2"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(242, 242, 242))
$ws2.Cells["A2"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
$ws2.Cells["A2"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
$ws2.Row(2).Height = 22

# Super Header Row 3
$ws2.Cells["A3:C3"].Merge = $true
$ws2.Cells["A3"].Value = "DANH MỤC & MÃ HỆ THỐNG CŨ (LEGACY PSS)"
$ws2.Cells["A3"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws2.Cells["A3"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
$ws2.Cells["A3"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws2.Cells["A3"].Style.Font.Bold = $true
$ws2.Cells["A3"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center

$ws2.Cells["D3:F3"].Merge = $true
$ws2.Cells["D3"].Value = "PHÂN CẤP SẢN PHẨM CŨ (LEVEL 1 - 2 - 3)"
$ws2.Cells["D3"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws2.Cells["D3"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(68, 114, 196))
$ws2.Cells["D3"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws2.Cells["D3"].Style.Font.Bold = $true
$ws2.Cells["D3"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center

$ws2.Cells["G3:I3"].Merge = $true
$ws2.Cells["G3"].Value = "QUY HOẠCH & MAPPING DATABRICKS MỚI"
$ws2.Cells["G3"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws2.Cells["G3"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(55, 86, 35))
$ws2.Cells["G3"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws2.Cells["G3"].Style.Font.Bold = $true
$ws2.Cells["G3"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center

$ws2.Cells["J3:L3"].Merge = $true
$ws2.Cells["J3"].Value = "TRẠNG THÁI & ĐÁNH GIÁ CHUYỂN ĐỔI"
$ws2.Cells["J3"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws2.Cells["J3"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(112, 48, 160))
$ws2.Cells["J3"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws2.Cells["J3"].Style.Font.Bold = $true
$ws2.Cells["J3"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
$ws2.Row(3).Height = 25

# Sub Header Row 4
$headers2 = @(
    "STT (No)",
    "Legacy Ancillary ID`n(ID Cũ)",
    "Charge Type Ident`n(Mã Cũ)",
    "Phân loại Cấp 1`n(Level 1)",
    "Phân loại Cấp 2`n(Level 2)",
    "Phân loại Cấp 3`n(Level 3)",
    "Nhóm sản phẩm mới`n(Target Group)",
    "Nguồn dữ liệu PSS`n(PSS Source)",
    "Logic nhận diện trên Databricks`n(Silver & Gold Layer)",
    "Trạng thái chuyển đổi`n(System Status)",
    "Độ khớp dữ liệu`n(Data Quality)",
    "Ghi chú nghiệp vụ & Phạm vi (Tiếng Việt)"
)

for ($c = 1; $c -le 12; $c++) {
    $cell = $ws2.Cells[4, $c]
    $cell.Value = $headers2[$c - 1]
    $cell.Style.Font.Bold = $true
    $cell.Style.Font.Size = 9.5
    $cell.Style.WrapText = $true
    $cell.Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
    $cell.Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
    $cell.Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
    
    if ($c -le 3) { $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(217, 225, 242)) }
    elseif ($c -le 6) { $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(222, 235, 247)) }
    elseif ($c -le 9) { $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(226, 239, 218)) }
    else { $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(225, 213, 231)) }
}
$ws2.Row(4).Height = 32

# Đọc bảng cũ nếu có
if (Test-Path $legacyExcelPath) {
    $legPkg = Open-ExcelPackage -Path $legacyExcelPath
    $legWs = $legPkg.Workbook.Worksheets["Ancillary Type"]
    $ignoreList = @('AI', 'SG', 'OO', 'OP', 'AS', 'APPS', 'BKK E8', 'SF', 'MO', 'FA')

    $validRows = @()
    for ($r = 2; $r -le $legWs.Dimension.Rows; $r++) {
        $id = $legWs.Cells[$r, 1].Value
        $ident = ("" + $legWs.Cells[$r, 2].Value).Trim()
        $l1 = ("" + $legWs.Cells[$r, 3].Value).Trim()
        $l2 = ("" + $legWs.Cells[$r, 4].Value).Trim()
        $l3 = ("" + $legWs.Cells[$r, 5].Value).Trim()
        if ([string]::IsNullOrWhiteSpace($ident) -or $id -le 0) { continue }
        if ($ignoreList -contains $ident) { continue }

        $validRows += [PSCustomObject]@{
            ID = $id; Ident = $ident; Level1 = $l1; Level2 = $l2; Level3 = $l3
        }
    }
    $legPkg.Dispose()

    # Function classify
    function Get-LegacyEnrichment($r) {
        $id = [int]$r.ID; $ident = ("" + $r.Ident).Trim()
        $l1 = ("" + $r.Level1).Trim(); $l2 = ("" + $r.Level2).Trim(); $l3 = ("" + $r.Level3).Trim()
        $section = ""; $group = ""; $source = ""; $dbLogic = ""; $status = ""; $quality = "100% Khớp"; $note = ""

        if ($ident -in @('BA', 'CB', 'QR') -or $l1 -in @('Baggage', 'Cabin Baggage') -or $l3 -like "*bag*" -or $l3 -like "*Oversize*") {
            $section = "SECTION 1: BAGGAGE & CABIN BAGGAGE"
            if ($ident -eq 'CB' -or $l1 -eq 'Cabin Baggage' -or $l2 -eq 'Cabin Bag') {
                $group = "Cabin Baggage"; $source = "Cả hai (Surcharge & SSR)"; $dbLogic = "Surcharge 'CB%', 'CBG%' / SSR category 'Cabin Baggage'"; $status = "Đã chuyển đổi (Silver Model)"; $note = "Hành lý xách tay mua thêm/quá cước (2kg, 7kg)"
            } elseif ($l3 -like "*Oversize*" -or $l2 -like "*Oversize*") {
                $group = "Oversize Baggage"; $source = "Cả hai (Surcharge & SSR)"; $dbLogic = "Pattern '%OSB%', '%OV%', '%OVERSIZE%' -> baggage_type = 'O'"; $status = "Đã chuyển đổi (Gold Comm)"; $note = "Hành lý quá khổ cồng kềnh (20kg, 30kg, dịch vụ sân bay FOVD/AOVD)"
            } elseif ($l3 -like "*gate*" -or $l2 -like "*gate*") {
                $group = "Gate Baggage"; $source = "PSS Surcharge"; $dbLogic = "Pattern '%GD', '%GI%', '%GATE%' -> baggage_category = 'Gate'"; $status = "Đã chuyển đổi (Gold Comm)"; $note = "Hành lý phạt/thu phí tại cửa khởi hành (Gate counter)"
            } elseif ($l2 -eq 'Purchase at port' -or $l3 -like "*counter*" -or $l3 -like "*Airport*") {
                $group = "Airport Baggage"; $source = "Cả hai (Surcharge & SSR)"; $dbLogic = "Surcharge '%ApD', '%ApI' / SSR Category 'Airport Baggage' (535, 536, 537)"; $status = "Đã chuyển đổi (Gold Comm)"; $note = "Hành lý mua trực tiếp tại quầy check-in sân bay (gói & kiện lẻ)"
            } elseif ($id -eq 1020 -or $ident -eq 'QR') {
                $group = "Baggage Interline"; $source = "PSS Surcharge"; $dbLogic = "surcharge_ident = 'QR' / GDS Interline Excess Bag"; $status = "Đã chuyển đổi"; $note = "Hành lý liên danh đối tác GDS Qatar Airways"
            } else {
                $group = "Prepaid Baggage"; $source = "Cả hai (Surcharge & SSR)"; $dbLogic = "Surcharge '20kINT%', '20kCON%' / SSR Category 'Baggage' (15kg - 100kg)"; $status = "Đã chuyển đổi (Silver Model)"; $note = "Hành lý ký gửi mua trước qua Web/App/Đại lý"
            }
        } elseif ($ident -eq 'SA' -or $l1 -eq 'Seat Assignment') {
            $section = "SECTION 2: SEAT ASSIGNMENT"; $group = "Seat Assignment"; $source = "Cả hai (Surcharge & SSR)"
            if ($l2 -eq 'STAFF') { $dbLogic = "Surcharge / SSR Seat nội bộ nhân viên Vietjet"; $status = "Đã chuyển đổi"; $note = "Chỗ ngồi ưu đãi cho cán bộ nhân viên hãng" }
            elseif ($l3 -like "*Empty*") { $dbLogic = "Surcharge 'ES1', 'ES2' / Ghế trống liền kề"; $status = "Đã chuyển đổi"; $note = "Dịch vụ mua thêm ghế trống kế bên (Empty Seat)" }
            elseif ($l2 -eq 'Purchase at port') { $dbLogic = "Surcharge chọn ghế tại quầy check-in sân bay"; $status = "Đã chuyển đổi"; $note = "Chọn chỗ ngồi trực tiếp tại sân bay lúc làm thủ tục" }
            else { $dbLogic = "Surcharge / SSR Seat Definition (Hot, Front, Normal Seat)"; $status = "Đã chuyển đổi"; $note = "Chọn ghế trước chuyến bay: Ghế đầu hàng, Thoát hiểm, Ghế thường" }
        } elseif ($l1 -eq 'Meal' -or $l2 -like "Combo*") {
            $section = "SECTION 3: MEALS & BEVERAGES"; $group = "Meals & Beverages"; $source = "PSS SSR (ssr_definition)"; $dbLogic = "ssr_category_name = 'Meal' / ssr_name LIKE 'Combo%'"; $status = "Đã chuyển đổi (Silver SSR)"; $note = "Suất ăn nóng đặt trước: Cơm, Phở, Bánh mì, Cà ri, Món chay, Đồ uống"
        } elseif ($l1 -eq 'Priority checkin' -or $ident -eq 'SP' -or $ident -eq 'QT' -or $ident -eq 'CS') {
            $section = "SECTION 4: PRIORITY & AIRPORT CONVENIENCE SERVICES"; $source = "Cả hai (Surcharge & SSR)"
            if ($ident -eq 'SP') { $group = "SkyBoss Lounge & Service"; $dbLogic = "surcharge_ident = 'SP' / Gói dịch vụ SkyBoss Plus"; $status = "Đã chuyển đổi"; $note = "Gói quyền lợi cao cấp SkyBoss (Phòng chờ, Xe đưa đón, Ưu tiên)" }
            elseif ($ident -eq 'CS') { $group = "Connecting Service"; $dbLogic = "surcharge_ident = 'CS' / Phí hỗ trợ nối chuyến"; $status = "Đã chuyển đổi"; $note = "Dịch vụ hỗ trợ chuyển tiếp chuyến bay (Transit/Connecting)" }
            elseif ($ident -eq 'QT') { $group = "Quick Ticket"; $dbLogic = "surcharge_ident = 'QT' / Phí xuất vé nhanh"; $status = "Đã chuyển đổi"; $note = "Dịch vụ giữ chỗ và xuất vé gấp trong vòng 24h" }
            else { $group = "Priority Check-in"; $dbLogic = "ssr_category_name = 'Priority Checkin' / Surcharge 'PC%'"; $status = "Đã chuyển đổi"; $note = "Dịch vụ làm thủ tục ưu tiên tại quầy riêng sân bay" }
        } elseif ($ident -in @('SV', 'IF', 'NL') -or $l1 -eq 'Special Service') {
            $section = "SECTION 5: SPECIAL SERVICES"; $group = "Special Passenger Services"; $source = "Cả hai (Surcharge & SSR)"
            if ($ident -eq 'IF') { $dbLogic = "surcharge_ident = 'IF' / Infant Fee"; $status = "Đã chuyển đổi"; $note = "Phí phục vụ em bé dưới 2 tuổi (Infant without seat)" }
            elseif ($ident -eq 'NL') { $dbLogic = "surcharge_ident = 'NL' / Not to land charge"; $status = "Đã chuyển đổi"; $note = "Phí hành khách không được phép nhập cảnh do quy định nhà chức trách" }
            else { $dbLogic = "SSR pax_requests / Surcharge 'SV%'"; $status = "Đã chuyển đổi"; $note = "Dịch vụ đặc biệt: Thú cưng trên cabin (PETC), Trẻ em đi một mình (UM/YPTA), Đón tiễn" }
        } elseif ($ident -in @('IN', 'IT') -or $l1 -like "*Insurance*") {
            $section = "SECTION 6: TRAVEL INSURANCE"; $group = "Travel & Baggage Insurance"; $source = "PSS Surcharge (surcharge_ident)"; $dbLogic = "surcharge_ident IN ('IN', 'IT', 'MC') / Đối tác HDI Bảo hiểm"; $status = "Đã chuyển đổi"; $note = "Bảo hiểm du lịch trọn gói & Bảo hiểm thất lạc hành lý HDI (Nội địa & Quốc tế)"
        } elseif ($ident -eq 'MC' -or $l1 -like "*Merchandise*") {
            $section = "SECTION 7: INFLIGHT MERCHANDISE & DUTY FREE"; $group = "Airport & Inflight Merchandise"; $source = "PSS Surcharge"; $dbLogic = "surcharge_ident = 'MC' / Quấn vali sân bay"; $status = "Đã chuyển đổi"; $note = "Hàng lưu niệm trên máy bay & Dịch vụ quấn bọc hành lý tại sân bay"
        } elseif ($ident -in @('CX', 'MD', 'XX', 'UF', 'NR', 'PD', 'LT')) {
            $section = "SECTION 8: FLIGHT MODIFICATION, PENALTY & ADMIN FEES"; $group = "Changes, Penalty & Administrative Fees"; $source = "PSS Surcharge (gl_charges)"; $dbLogic = "surcharge_ident IN ('CX', 'MD', 'XX', 'UF', 'NR', 'PD', 'LT')"; $status = "Đã chuyển đổi"; $note = "Phí đổi vé (MD), Hủy vé (CX), Bỏ chuyến No-show (XX), Nâng hạng (UF), Phí giờ cao điểm (PD), Phí muộn (LT)"
        } else {
            $section = "SECTION 9: OTHER SYSTEM & LEGACY CHARGES"; $group = "Other System & Partner Fees"; $source = "PSS Surcharge / Hạch toán GL"; $dbLogic = "surcharge_ident IN ('$ident') / Phụ thu thanh toán & đối tác"; $status = "Đã phân loại"; $note = "Phí tiện ích thanh toán (PM), Phí quản trị (HA, AM, MF), Đối tác liên danh (JL, BR, CR), Bù trừ hạch toán (BL, WO, FC)"
        }

        return [PSCustomObject]@{
            Section = $section; ID = $id; Ident = $ident; Level1 = $l1; Level2 = $l2; Level3 = $l3
            ProductGroup = $group; DataSource = $source; DatabricksLogic = $dbLogic
            MigrationStatus = $status; DataQuality = $quality; Notes = $note
        }
    }

    $enriched = $validRows | ForEach-Object { Get-LegacyEnrichment $_ }

    $sectionOrder = @(
        "SECTION 1: BAGGAGE & CABIN BAGGAGE",
        "SECTION 2: SEAT ASSIGNMENT",
        "SECTION 3: MEALS & BEVERAGES",
        "SECTION 4: PRIORITY & AIRPORT CONVENIENCE SERVICES",
        "SECTION 5: SPECIAL SERVICES",
        "SECTION 6: TRAVEL INSURANCE",
        "SECTION 7: INFLIGHT MERCHANDISE & DUTY FREE",
        "SECTION 8: FLIGHT MODIFICATION, PENALTY & ADMIN FEES",
        "SECTION 9: OTHER SYSTEM & LEGACY CHARGES"
    )

    $r2Index = 5
    $globalStt = 1

    foreach ($sec in $sectionOrder) {
        $secRows = $enriched | Where-Object { $_.Section -eq $sec } | Sort-Object ID
        if ($secRows.Count -eq 0) { continue }

        $ws2.Cells["A$r2Index:L$r2Index"].Merge = $true
        $ws2.Cells["A$r2Index"].Value = "$sec ($($secRows.Count) danh mục)"
        $ws2.Cells["A$r2Index"].Style.Font.Bold = $true
        $ws2.Cells["A$r2Index"].Style.Font.Size = 10.5
        $ws2.Cells["A$r2Index"].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
        $ws2.Cells["A$r2Index"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
        $ws2.Cells["A$r2Index"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(230, 230, 230))
        $ws2.Cells["A$r2Index"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
        $ws2.Row($r2Index).Height = 22
        $r2Index++

        foreach ($item in $secRows) {
            $ws2.Cells[$r2Index, 1].Value = $globalStt
            $ws2.Cells[$r2Index, 1].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            $ws2.Cells[$r2Index, 2].Value = $item.ID
            $ws2.Cells[$r2Index, 2].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            $ws2.Cells[$r2Index, 3].Value = $item.Ident
            $ws2.Cells[$r2Index, 3].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            $ws2.Cells[$r2Index, 3].Style.Font.Bold = $true
            $ws2.Cells[$r2Index, 4].Value = $item.Level1
            $ws2.Cells[$r2Index, 5].Value = $item.Level2
            $ws2.Cells[$r2Index, 6].Value = $item.Level3
            $ws2.Cells[$r2Index, 7].Value = $item.ProductGroup
            $ws2.Cells[$r2Index, 8].Value = $item.DataSource
            $ws2.Cells[$r2Index, 9].Value = $item.DatabricksLogic
            $ws2.Cells[$r2Index, 10].Value = $item.MigrationStatus
            $ws2.Cells[$r2Index, 10].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            if ($item.MigrationStatus -like "*Đã chuyển đổi*") {
                $ws2.Cells[$r2Index, 10].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(55, 86, 35))
                $ws2.Cells[$r2Index, 10].Style.Font.Bold = $true
            } else {
                $ws2.Cells[$r2Index, 10].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
            }
            $ws2.Cells[$r2Index, 11].Value = $item.DataQuality
            $ws2.Cells[$r2Index, 11].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
            $ws2.Cells[$r2Index, 12].Value = $item.Notes

            for ($c = 1; $c -le 12; $c++) {
                $cell = $ws2.Cells[$r2Index, $c]
                $cell.Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
                $cell.Style.WrapText = $true
                $cell.Style.Border.Top.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Top.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Bottom.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Bottom.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Left.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Left.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
                $cell.Style.Border.Right.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
                $cell.Style.Border.Right.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
            }

            $globalStt++
            $r2Index++
        }
    }
}

for ($r = 3; $r -le 4; $r++) {
    for ($c = 1; $c -le 12; $c++) {
        $ws2.Cells[$r, $c].Style.Border.Top.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Medium
        $ws2.Cells[$r, $c].Style.Border.Bottom.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Medium
        $ws2.Cells[$r, $c].Style.Border.Left.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
        $ws2.Cells[$r, $c].Style.Border.Right.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
    }
}

$ws2.Column(1).Width = 7
$ws2.Column(2).Width = 12
$ws2.Column(3).Width = 12
$ws2.Column(4).Width = 22
$ws2.Column(5).Width = 28
$ws2.Column(6).Width = 28
$ws2.Column(7).Width = 24
$ws2.Column(8).Width = 22
$ws2.Column(9).Width = 35
$ws2.Column(10).Width = 24
$ws2.Column(11).Width = 14
$ws2.Column(12).Width = 45

$ws2.View.FreezePanes(5, 4)
$ws2.View.ShowGridLines = $true

# ------------------------------------------------------------------------------
# SHEET 3: Databricks_Medallion_Views
# ------------------------------------------------------------------------------
$ws3Name = "Databricks_Medallion_Views"
$existingWs3 = $excel.Workbook.Worksheets[$ws3Name]
if ($existingWs3) { $excel.Workbook.Worksheets.Delete($existingWs3) }

$ws3 = $excel.Workbook.Worksheets.Add($ws3Name)
$ws3.Cells.Style.Font.Name = "Segoe UI"
$ws3.Cells.Style.Font.Size = 10

# Title Row 1
$ws3.Cells["A1:H1"].Merge = $true
$ws3.Cells["A1"].Value = "KIẾN TRÚC DATABRICKS MEDALLION & CÁC VIEWS CHUYỂN ĐỔI TỪ GL CHARGES"
$ws3.Cells["A1"].Style.Font.Size = 14
$ws3.Cells["A1"].Style.Font.Bold = $true
$ws3.Cells["A1"].Style.Font.Color.SetColor([System.Drawing.Color]::White)
$ws3.Cells["A1"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws3.Cells["A1"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120))
$ws3.Cells["A1"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
$ws3.Cells["A1"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
$ws3.Row(1).Height = 35

# Subtitle Row 2
$ws3.Cells["A2:H2"].Merge = $true
$ws3.Cells["A2"].Value = "Quy hoạch 5 views Silver & Gold thay thế Stored Procedure cũ, phân tách rõ ràng trách nhiệm giữa Master Data, Booking Charges và Báo cáo Hoa hồng"
$ws3.Cells["A2"].Style.Font.Size = 10
$ws3.Cells["A2"].Style.Font.Italic = $true
$ws3.Cells["A2"].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(89, 89, 89))
$ws3.Cells["A2"].Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
$ws3.Cells["A2"].Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(242, 242, 242))
$ws3.Cells["A2"].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
$ws3.Cells["A2"].Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
$ws3.Row(2).Height = 22

# Header Row 3
$headers3 = @(
    "STT",
    "Tầng dữ liệu`n(Layer)",
    "Tên View trên Databricks`n(View Name)",
    "Vai trò nghiệp vụ & Mục tiêu`n(Business Role & Scope)",
    "Bảng nguồn dữ liệu`n(Source Tables / Joins)",
    "Logic nhận diện & Regex quan trọng`n(Key Logic & Regex)",
    "Quy tắc tính toán & Nghiệp vụ`n(Business Rules)",
    "Trạng thái & File DDL lưu trữ`n(DDL File)"
)

for ($c = 1; $c -le 8; $c++) {
    $cell = $ws3.Cells[3, $c]
    $cell.Value = $headers3[$c - 1]
    $cell.Style.Font.Bold = $true
    $cell.Style.Font.Size = 9.5
    $cell.Style.WrapText = $true
    $cell.Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
    $cell.Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
    $cell.Style.Fill.PatternType = [OfficeOpenXml.Style.ExcelFillStyle]::Solid
    $cell.Style.Fill.BackgroundColor.SetColor([System.Drawing.Color]::FromArgb(47, 84, 150))
    $cell.Style.Font.Color.SetColor([System.Drawing.Color]::White)
    $cell.Style.Border.Top.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Medium
    $cell.Style.Border.Bottom.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Medium
    $cell.Style.Border.Left.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
    $cell.Style.Border.Right.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
}
$ws3.Row(3).Height = 32

$viewSpecs = @(
    [PSCustomObject]@{
        Layer = "Silver Models"; ViewName = "silver_dev.models.pss_surcharge"
        Role = "Chuẩn hóa Master data Surcharge & Bóc tách số kg tự động"; Sources = "silver.src_pssdb.surcharge"
        Regex = "- DATEADD(HOUR, 7, last_mod_date)`n- Bóc tách kg: TRY_CAST(REGEXP_EXTRACT(surcharge_desc, '(\\d{1,3})\\s*kg', 1) AS INT)"
        Rules = "Loại bỏ hardcode ID, chuẩn hóa múi giờ UTC+7 cho ngày cập nhật"; DDL = "silver_dev.models.pss_surcharge.txt"
    },
    [PSCustomObject]@{
        Layer = "Silver Models"; ViewName = "silver_dev.models.pss_ssr_detail"
        Role = "Chuẩn hóa Master data SSR kết hợp SSR Category & IATA requests"
        Sources = "silver_dev.src_pssdb.ssr_definition (SSR_D)`nJOIN SSR_Category (SSR_C)`nJOIN pax_requests_definition (PRD)"
        Regex = "- TRY_CAST(REGEXP_EXTRACT(ssr_description, '(\\d{1,3})\\s*kg', 1) AS INT)`n- ssr_category_name mapping"
        Rules = "Bổ sung đầy đủ Category Name, Active flags, Commission type và IATA code phục vụ join động"; DDL = "silver_dev.models.pss_ssr_detail.txt"
    },
    [PSCustomObject]@{
        Layer = "Silver Analytics"; ViewName = "silver_dev.analytics.gl_booking_charges"
        Role = "Hợp nhất chi tiết giao dịch charges với chặng bay kết nối và Master Data"
        Sources = "models.pss_res_charges (CH)`nLEFT JOIN cte_res_leg_connecting (RL)`nLEFT JOIN models.pss_res_header (RH)`nLEFT JOIN models.pss_surcharge (sur)`nLEFT JOIN models.pss_ssr_detail (ssr)"
        Regex = "- Mapping Factor cho chặng bay nối chuyến (connecting_flag = 'Y')`n- Bóc tách tự động baggage_kg từ sur/ssr`n- Phân bổ thuế sân bay AIRPORT_TAX cho chặng đầu"
        Rules = "Xóa bỏ prefix str_, dtm_, lng_. Thay thế case-when ID bằng Master Data joins trực tiếp. Tính lại tỷ giá (1 / exchange_rate)."; DDL = "silver_dev.analytics.gl_booking_charges.txt"
    },
    [PSCustomObject]@{
        Layer = "Gold Shared"; ViewName = "gold_dev.shared.gl_charges"
        Role = "Bảng dữ liệu dùng chung (Data Mart) phục vụ toàn bộ phòng ban Tài chính & Báo cáo GL"
        Sources = "silver_dev.analytics.gl_booking_charges`nLEFT JOIN sked_detail / agency mapping"
        Regex = "- str_flight_type -> sked.route_type ('Domestic' / 'International')`n- Lấy agency_name & channel trực tiếp từ Agency Mapping"
        Rules = "Chuẩn hóa hoàn toàn tên cột theo chuẩn Analytics Databricks, hiển thị sẵn thông tin SSR và Surcharge để các bên truy vấn không cần re-join."; DDL = "gold_dev.shared.gl_charges.txt"
    },
    [PSCustomObject]@{
        Layer = "Gold Commission"; ViewName = "gold_dev.com.ancillary_commission_baggage_detail"
        Role = "Báo cáo chi tiết & Tính tiền hoa hồng hành lý sân bay theo KPI SAN BAY"
        Sources = "gold_dev.shared.gl_charges (c)"
        Regex = "- Gate vs Counter: LIKE '%GD', '%GI%', '%GATE%', 'CBG%' -> 'Gate'`n- Baggage Type: LIKE '%OSB%', '%OV%' -> 'O'; LIKE '%EX%' -> 'L'; Còn lại -> 'G'`n- Trích xuất baggage_kg đa tầng"
        Rules = "Áp chính sách chi hoa hồng chuẩn theo Tờ trình:`n+ Counter G: DOM 8,000 / INT 12,000`n+ Counter L: DOM 3,000/kg / INT 5,000/kg`n+ Gate G: DOM 5,000 / INT 10,000`n+ Gate L: DOM 2,000/kg / INT 4,000/kg`n+ Oversize O: DOM 30,000 / INT 60,000"; DDL = "gold_dev.com.ancillary_commission_baggage_detail.txt"
    }
)

$r3Index = 4
$stt3 = 1
foreach ($v in $viewSpecs) {
    $ws3.Cells[$r3Index, 1].Value = $stt3
    $ws3.Cells[$r3Index, 1].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
    $ws3.Cells[$r3Index, 2].Value = $v.Layer
    $ws3.Cells[$r3Index, 2].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center
    $ws3.Cells[$r3Index, 2].Style.Font.Bold = $true
    if ($v.Layer -like "Gold*") { $ws3.Cells[$r3Index, 2].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(192, 0, 0)) }
    else { $ws3.Cells[$r3Index, 2].Style.Font.Color.SetColor([System.Drawing.Color]::FromArgb(31, 78, 120)) }

    $ws3.Cells[$r3Index, 3].Value = $v.ViewName
    $ws3.Cells[$r3Index, 3].Style.Font.Bold = $true
    $ws3.Cells[$r3Index, 4].Value = $v.Role
    $ws3.Cells[$r3Index, 5].Value = $v.Sources
    $ws3.Cells[$r3Index, 6].Value = $v.Regex
    $ws3.Cells[$r3Index, 7].Value = $v.Rules
    $ws3.Cells[$r3Index, 8].Value = $v.DDL
    $ws3.Cells[$r3Index, 8].Style.HorizontalAlignment = [OfficeOpenXml.Style.ExcelHorizontalAlignment]::Center

    for ($c = 1; $c -le 8; $c++) {
        $cell = $ws3.Cells[$r3Index, $c]
        $cell.Style.VerticalAlignment = [OfficeOpenXml.Style.ExcelVerticalAlignment]::Center
        $cell.Style.WrapText = $true
        $cell.Style.Border.Top.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
        $cell.Style.Border.Top.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
        $cell.Style.Border.Bottom.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
        $cell.Style.Border.Bottom.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
        $cell.Style.Border.Left.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
        $cell.Style.Border.Left.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
        $cell.Style.Border.Right.Style = [OfficeOpenXml.Style.ExcelBorderStyle]::Thin
        $cell.Style.Border.Right.Color.SetColor([System.Drawing.Color]::FromArgb(217, 217, 217))
    }
    $stt3++
    $r3Index++
}

$ws3.Column(1).Width = 7
$ws3.Column(2).Width = 18
$ws3.Column(3).Width = 38
$ws3.Column(4).Width = 32
$ws3.Column(5).Width = 32
$ws3.Column(6).Width = 38
$ws3.Column(7).Width = 36
$ws3.Column(8).Width = 35

$ws3.View.FreezePanes(4, 4)
$ws3.View.ShowGridLines = $true

$excel.Save()
$excel.Dispose()

Write-Host "Consolidated workbook updated successfully at: $excelPath"
