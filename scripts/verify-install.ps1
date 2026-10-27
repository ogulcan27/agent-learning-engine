<#
.SYNOPSIS
    Verify an installed Stay in the Loop skill (stay-in-the-loop) against the distribution manifest.

.DESCRIPTION
    Calls install.ps1 in verify mode. Writes nothing.
    Checks: target exists, SKILL.md exists, file set equals the manifest, SHA256 of every file,
    no extra file (for example project state) inside the skill directory.
    Output: PASS or FAIL (FAIL also gives a non-zero exit code).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Project', 'Personal')][string]$Scope,
    [string]$ProjectPath,
    [string]$Repository,
    [string]$Ref,
    [string]$Archive,
    [string]$BaseUrl = 'https://github.com'
)
$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'install.ps1') @PSBoundParameters -VerifyOnly
