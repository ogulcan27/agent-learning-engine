<#
.SYNOPSIS
    Update an existing Agent Learning Engine learning skill install.

.DESCRIPTION
    Calls install.ps1 in update mode. Same parameters and source modes as install.ps1.
    Needs an existing install. Atomic replace with rollback.
    Does not touch docs/learning/ or the Personal Technical Library. No state migration in 1.0.0.
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
& (Join-Path $PSScriptRoot 'install.ps1') @PSBoundParameters -Update
