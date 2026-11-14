param(
    [switch]$SkipMcp
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$copilotHome = Join-Path $HOME '.copilot'
$skillsRoot = Join-Path $copilotHome 'skills'
$agentsRoot = Join-Path $copilotHome 'agents'
$sourceAgents = Join-Path $repoRoot '.copilot\agents'
$binRoot = Join-Path $copilotHome 'bin'

$skillNames = @(
    'app-packager',
    'gitops-gatekeeper',
    'lead-architect',
    'lead-ba',
    'lead-backend',
    'lead-cyber-security',
    'lead-frontend',
    'lead-pm',
    'lead-qa',
    'master-agent',
    'web-search-interactive'
)

function Set-DirectoryLink {
    param(
        [string]$LinkPath,
        [string]$TargetPath
    )

    if (Test-Path -LiteralPath $LinkPath) {
        $existing = Get-Item -LiteralPath $LinkPath -Force
        if ($existing.LinkType -and $existing.Target -contains $TargetPath) {
            return
        }
        throw "Destination already exists and was left unchanged: $LinkPath"
    }

    New-Item -ItemType Junction -Path $LinkPath -Target $TargetPath | Out-Null
}

New-Item -ItemType Directory -Path $copilotHome, $skillsRoot -Force | Out-Null

foreach ($name in $skillNames) {
    if ($name -eq 'master-agent') {
        $source = Join-Path $repoRoot '.copilot\skills\master-agent'
    }
    else {
        $source = Join-Path $repoRoot "common\skills\$name"
    }

    if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) {
        throw "Required skill file is missing: $source"
    }

    Set-DirectoryLink -LinkPath (Join-Path $skillsRoot $name) -TargetPath $source
}

$managedAgents = $false
if (Test-Path -LiteralPath $agentsRoot) {
    $existingAgents = Get-Item -LiteralPath $agentsRoot -Force
    if ($existingAgents.LinkType -and $existingAgents.Target -contains $sourceAgents) {
        $managedAgents = $true
    }
}
else {
    New-Item -ItemType Junction -Path $agentsRoot -Target $sourceAgents | Out-Null
    $managedAgents = $true
}

if (-not $managedAgents) {
    $manifestPath = Join-Path $copilotHome 'agent-hub-manifest.json'
    if (Test-Path -LiteralPath $manifestPath) {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    }
    else {
        $manifest = [pscustomobject]@{}
    }

    foreach ($agent in Get-ChildItem -LiteralPath $sourceAgents -File -Filter '*.agent.md') {
        $linkPath = Join-Path $agentsRoot $agent.Name
        $sourceHash = (Get-FileHash -LiteralPath $agent.FullName -Algorithm SHA256).Hash
        if (Test-Path -LiteralPath $linkPath) {
            $installedHash = (Get-FileHash -LiteralPath $linkPath -Algorithm SHA256).Hash
            $previousHash = $manifest.PSObject.Properties[$agent.Name]
            if ($installedHash -ne $sourceHash -and
                (-not $previousHash -or $installedHash -ne $previousHash.Value)) {
                throw "Agent destination differs from the managed copy and was left unchanged: $linkPath"
            }
        }

        Copy-Item -LiteralPath $agent.FullName -Destination $linkPath -Force
        $manifest | Add-Member -NotePropertyName $agent.Name -NotePropertyValue $sourceHash -Force
    }

    Set-Content -LiteralPath $manifestPath -Value ($manifest | ConvertTo-Json -Depth 10) -Encoding UTF8
}

if (-not $SkipMcp) {
    $mcpDirectory = Join-Path $repoRoot 'common\mcp\web-search-interactive'
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    $python = Get-Command python -ErrorAction SilentlyContinue

    if ($uv) {
        $command = $uv.Source
        $arguments = @('run', '--directory', $mcpDirectory, '--no-project', 'python', 'server.py')
    }
    elseif ($python) {
        $command = $python.Source
        $arguments = @('server.py')
    }
    else {
        throw 'Install Python or uv and rerun this script to configure the MCP server.'
    }

    $configPath = Join-Path $copilotHome 'mcp-config.json'
    if (Test-Path -LiteralPath $configPath) {
        $configText = Get-Content -LiteralPath $configPath -Raw
        $config = $configText | ConvertFrom-Json
    }
    else {
        $config = [pscustomobject]@{}
    }

    if (-not $config.PSObject.Properties['mcpServers']) {
        $config | Add-Member -NotePropertyName 'mcpServers' -NotePropertyValue ([pscustomobject]@{})
    }

    $serverConfig = [pscustomobject]@{
        type    = 'stdio'
        command = $command
        args    = $arguments
        cwd     = $mcpDirectory
    }
    $existingServer = $config.mcpServers.PSObject.Properties['web-search-interactive']
    $needsUpdate = -not $existingServer
    if ($existingServer) {
        $existingArgs = @($existingServer.Value.args) -join "`0"
        $desiredArgs = @($arguments) -join "`0"
        $needsUpdate = $existingServer.Value.type -ne $serverConfig.type -or
            $existingServer.Value.command -ne $serverConfig.command -or
            $existingServer.Value.cwd -ne $serverConfig.cwd -or
            $existingArgs -ne $desiredArgs
    }

    if ($needsUpdate) {
        $config.mcpServers | Add-Member -NotePropertyName 'web-search-interactive' -NotePropertyValue $serverConfig -Force
        $newConfigText = ($config | ConvertTo-Json -Depth 20) + [Environment]::NewLine
        if (Test-Path -LiteralPath $configPath) {
            $backup = "$configPath.$(Get-Date -Format 'yyyyMMddHHmmss').bak"
            Copy-Item -LiteralPath $configPath -Destination $backup
            Write-Host "Existing MCP config backed up to: $backup"
        }
        Set-Content -LiteralPath $configPath -Value $newConfigText -Encoding UTF8
    }

    $env:AGENT_HUB_ROOT = $repoRoot
    [Environment]::SetEnvironmentVariable('AGENT_HUB_ROOT', $repoRoot, 'User')
    $offloadSource = Join-Path $repoRoot 'common\scripts\gemini_offload_file.ps1'
    if (-not (Test-Path -LiteralPath $offloadSource -PathType Leaf)) {
        throw "Required Gemini offload helper is missing: $offloadSource"
    }
    New-Item -ItemType Directory -Path $binRoot -Force | Out-Null
    $offloadLauncher = Join-Path $binRoot 'agent-hub-gemini-offload.ps1'
    Copy-Item -LiteralPath $offloadSource -Destination $offloadLauncher -Force
}

Write-Host "Installed $($skillNames.Count) shared skills and $((Get-ChildItem -LiteralPath $sourceAgents -File -Filter '*.agent.md').Count) shared agents."
if (-not $SkipMcp) {
    Write-Host 'Configured the web-search-interactive MCP for this machine.'
    Write-Host 'Installed the Gemini file-offload launcher under the personal Copilot folder.'
}
Write-Host 'Open a new Copilot chat to reload customizations.'
