param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$CliPath = Join-Path $RootDir "capability-orchestrator\scripts\codex_skills.py"

python $CliPath @Args
exit $LASTEXITCODE
