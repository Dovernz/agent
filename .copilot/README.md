# Copilot global agent setup

This folder contains the Copilot-specific master skill, shared custom agents,
and a per-machine installer. The reusable specialist skills remain maintained
in `common/skills`.

## Install on this machine or another Windows machine

On a new Windows machine, clone the repository, open PowerShell in its root,
and run:

```powershell
git clone https://github.com/Dovernz/agent.git
Set-Location .\agent
.\.copilot\install.ps1
```

For an existing clone, run `git pull` first and then rerun the installer.

The installer links shared skills and agent definitions into the current user's
`%USERPROFILE%\.copilot\` folders and generates the local MCP configuration with
the current repository path and available Python/uv runtime. It preserves other
MCP server entries and backs up the existing MCP file before updating it. Use
`-SkipMcp` to install only skills and agents.

The web-search MCP exposes web retrieval and browser actions. Browser login/form
submission can access credentials in the hub's `.env`; do not invoke those
actions unless the user requested and confirmed the specific operation.

Copilot discovers these user skills and agents from the personal folders above;
it does not use the hub's `skills.json` shard to select them. Dynamic sharding
applies to Antigravity only. Skill bodies load on demand, while names and short
descriptions remain available for discovery. Keep project-specific instructions
in the active repository rather than adding them to global skills.

## What syncs with the Copilot account?

These customizations do **not** automatically follow the GitHub Copilot account
or VS Code Settings Sync. To use them on another computer, sync/clone this
repository there and run the installer. VS Code Settings Sync can synchronize
some VS Code profile settings and MCP configurations created in its profile
store, but not the native Copilot `~/.copilot/skills`, `~/.copilot/agents`, or
`~/.copilot/mcp-config.json` installed here. Each computer needs the repository
and its own compatible Python or uv runtime. Playwright/Chromium are optional
prerequisites for interactive-browser MCP tools; HTTP search tools do not
require them.
