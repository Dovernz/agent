<#
.SYNOPSIS
    Profiles input workspace files for the Multi-Agent Requirement & Excel Analysis System.
.DESCRIPTION
    Scans specified directories or files, identifies file formats (SQL, DOCX, XLSX, CSV),
    extracts structural metadata (line count, size, sheets, headers), and outputs an inventory
    JSON designed for task assignment across subagents.
#>

param(
    [string]$TargetFolder = ".",
    [string]$OutputFile = "file_inventory.json"
)

$ErrorActionPreference = 'SilentlyContinue'

$folder = (Resolve-Path $TargetFolder).Path
Write-Host "Scanning workspace files in: $folder"

$files = Get-ChildItem -Path $folder -File -Recurse | Where-Object {
    $_.FullName -notmatch '\\\.agent\\|\\\.git\\|\\\.system_generated\\'
}

$inventory = @()

foreach ($f in $files) {
    $ext = $f.Extension.ToLower()
    $type = "Unknown"
    $meta = @{}
    $assignedAgent = ""

    switch ($ext) {
        ".sql" {
            $type = "SQL Code / Procedure"
            $assignedAgent = "code-analyzer"
            $lines = (Get-Content -LiteralPath $f.FullName).Count
            $meta["Lines"] = $lines
        }
        ".txt" {
            if ($f.Name -match "silver|gold|gl_|view|model") {
                $type = "SQL DDL / View Definition"
                $assignedAgent = "code-analyzer"
            } else {
                $type = "Text / Requirements Note"
                $assignedAgent = "policy-doc-reader"
            }
            $meta["Lines"] = (Get-Content -LiteralPath $f.FullName).Count
        }
        ".docx" {
            $type = "Word Policy / Proposal Document"
            $assignedAgent = "policy-doc-reader"
            $meta["SizeBytes"] = $f.Length
        }
        ".csv" {
            $type = "CSV Master Data / Extract"
            $assignedAgent = "data-catalog-inspector"
            $firstLine = (Get-Content -LiteralPath $f.FullName -Head 1)
            $meta["Headers"] = $firstLine
            $meta["ApproxRows"] = (Get-Content -LiteralPath $f.FullName).Count
        }
        ".xlsx" {
            $type = "Excel Catalog / Report"
            $assignedAgent = "data-catalog-inspector"
            try {
                $pkg = Open-ExcelPackage -Path $f.FullName
                $sheets = ($pkg.Workbook.Worksheets | ForEach-Object { $_.Name }) -join ", "
                $meta["Sheets"] = $sheets
                $pkg.Dispose()
            } catch {
                $meta["Sheets"] = "Locked/Error"
            }
        }
    }

    if ($assignedAgent -ne "") {
        $inventory += [PSCustomObject]@{
            FileName = $f.Name
            RelativePath = $f.FullName.Replace($folder, "").TrimStart("\")
            Format = $ext
            Type = $type
            SizeKB = [Math]::Round($f.Length / 1KB, 1)
            AssignedSubagent = $assignedAgent
            Metadata = $meta
        }
    }
}

$json = $inventory | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($OutputFile, $json, [System.Text.Encoding]::UTF8)

Write-Host "Inventory completed with $($inventory.Count) relevant files."
Write-Host "Saved to: $OutputFile"
$inventory | Format-Table FileName, Format, Type, AssignedSubagent, SizeKB -AutoSize
