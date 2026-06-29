param(
    [ValidateSet("", "global", "local")]
    [string]$Scope = ""
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillName = "capability-orchestrator"
$SourceDir = Join-Path $RootDir $SkillName

if (-not (Test-Path -LiteralPath $SourceDir -PathType Container)) {
    Write-Error "The $SkillName directory was not found next to install.ps1"
    exit 1
}

switch ($Scope) {
    "global" {
        $Choice = "1"
    }
    "local" {
        $Choice = "2"
    }
    default {
        Write-Host "Install Codex Capability Orchestrator Skills"
        Write-Host ""
        Write-Host "Choose install location:"
        Write-Host "  1) Global Codex skills (~\.codex\skills)"
        Write-Host "  2) Local project skills (.\.codex\skills)"
        Write-Host ""

        $Choice = Read-Host "Enter 1 or 2 [1]"
        if ([string]::IsNullOrWhiteSpace($Choice)) {
            $Choice = "1"
        }
    }
}

switch ($Choice) {
    "1" {
        if ($env:CODEX_HOME) {
            $TargetRoot = Join-Path $env:CODEX_HOME "skills"
        } else {
            $TargetRoot = Join-Path $env:USERPROFILE ".codex\skills"
        }
    }
    "2" {
        $TargetRoot = Join-Path (Get-Location) ".codex\skills"
    }
    default {
        Write-Error "Expected 1 or 2"
        exit 1
    }
}

$TargetDir = Join-Path $TargetRoot $SkillName

New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
if (Test-Path -LiteralPath $TargetDir) {
    Remove-Item -LiteralPath $TargetDir -Recurse -Force
}
Copy-Item -LiteralPath $SourceDir -Destination $TargetDir -Recurse -Force

Write-Host ""
Write-Host "Installed $SkillName to:"
Write-Host "  $TargetDir"
