<#
.SYNOPSIS
    Remove the Stay in the Loop skill (stay-in-the-loop) from one scope.

.DESCRIPTION
    Removes only <base>/.claude/skills/stay-in-the-loop/.
      -Scope Project   <ProjectPath>/.claude/skills/stay-in-the-loop/   (default: current directory)
      -Scope Personal  <home>/.claude/skills/stay-in-the-loop/
    Never removes docs/learning/ or the Personal Technical Library.
    The skill directory is first moved aside (one rename), then deleted, so a failure leaves the old install intact.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Project', 'Personal')][string]$Scope,
    [string]$ProjectPath
)
$ErrorActionPreference = 'Stop'

if ($Scope -eq 'Personal') {
    $base = if ($env:USERPROFILE) { $env:USERPROFILE } else { $env:HOME }
    if (-not $base) { throw 'Cannot resolve the user home directory.' }
}
else {
    $base = if ($ProjectPath) { $ProjectPath } else { (Get-Location).Path }
    if (-not (Test-Path -LiteralPath $base -PathType Container)) { throw "Project path not found: $base" }
}
$target = Join-Path $base '.claude/skills/stay-in-the-loop'

if (Test-Path -LiteralPath $target) {
    $trash = Join-Path $base ".claude/.stay-in-the-loop-uninstall-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
    [IO.Directory]::Move($target, $trash)
    Remove-Item -LiteralPath $trash -Recurse -Force
    Write-Output "REMOVED: $target"
}
else {
    Write-Output "NOT INSTALLED: $target"
}
Write-Output 'Learning state retained.'
Write-Output 'Personal Technical Library retained.'
