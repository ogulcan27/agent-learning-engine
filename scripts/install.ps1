<#
.SYNOPSIS
    Install, update or verify the Claude Learning Skill.

.DESCRIPTION
    Target (the only path this script owns):
      -Scope Project   <ProjectPath>/.claude/skills/learning/   (default: current directory)
      -Scope Personal  <home>/.claude/skills/learning/

    Source modes:
      LOCAL    default; the development repository that holds this script
      ARCHIVE  -Archive <release zip>
      REMOTE   -Repository <owner/repo> -Ref <tag-or-commit>  (GitHub source archive)

    Flow: SOURCE -> MANIFEST/HASH VERIFY -> TARGET CHECK -> STAGE -> VERIFY
          -> OLD TARGET TO BACKUP -> STAGE TO TARGET -> VERIFY TARGET -> DELETE BACKUP.
    Any failure after the backup step restores the old target.
    The script never writes docs/learning/, the personal library, CLAUDE.md or other skills.

    Test-only fault injection: $env:LEARNING_SKILL_TEST_FAULT = stage | replace | verify.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('Project', 'Personal')][string]$Scope,
    [string]$ProjectPath,
    [string]$Repository,
    [string]$Ref,
    [string]$Archive,
    [string]$BaseUrl = 'https://github.com',
    [switch]$Update,
    [switch]$Force,
    [switch]$VerifyOnly
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$SkillRel = '.claude/skills/learning'

function Get-TargetBase {
    if ($Scope -eq 'Personal') {
        $homeDir = if ($env:USERPROFILE) { $env:USERPROFILE } else { $env:HOME }
        if (-not $homeDir) { throw 'Cannot resolve the user home directory.' }
        return $homeDir
    }
    $p = if ($ProjectPath) { $ProjectPath } else { (Get-Location).Path }
    if (-not (Test-Path -LiteralPath $p -PathType Container)) { throw "Project path not found: $p" }
    (Resolve-Path -LiteralPath $p).Path
}

function Expand-ToRoot([string]$Zip, [string]$Dest) {
    <# Extract a zip. Return the directory that holds .claude/skills/learning. #>
    [IO.Compression.ZipFile]::ExtractToDirectory($Zip, $Dest)
    if (Test-Path -LiteralPath (Join-Path $Dest $SkillRel)) { return $Dest }
    $dirs = @(Get-ChildItem -LiteralPath $Dest -Directory)
    if ($dirs.Count -eq 1 -and (Test-Path -LiteralPath (Join-Path $dirs[0].FullName $SkillRel))) { return $dirs[0].FullName }
    throw "Archive does not contain $SkillRel"
}

function Get-SourceRoot([string]$Work) {
    if ($Repository) {
        if (-not $Ref) { throw 'REMOTE mode needs -Ref <tag-or-commit>.' }
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        $url = "$($BaseUrl.TrimEnd('/'))/$Repository/archive/$Ref.zip"
        $zip = Join-Path $Work 'source.zip'
        Write-Host "Download: $url"
        Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
        return Expand-ToRoot $zip (Join-Path $Work 'source')
    }
    if ($Archive) {
        if (-not (Test-Path -LiteralPath $Archive -PathType Leaf)) { throw "Archive not found: $Archive" }
        return Expand-ToRoot (Resolve-Path -LiteralPath $Archive).Path (Join-Path $Work 'source')
    }
    if (-not $PSScriptRoot) { throw 'LOCAL mode needs the script file. For a remote run pass -Repository and -Ref.' }
    Split-Path -Parent $PSScriptRoot
}

function Read-Manifest([string]$Root) {
    $path = Join-Path $Root 'distribution/manifest.json'
    if (-not (Test-Path -LiteralPath $path)) { throw "Manifest not found: $path" }
    $m = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
    if ($m.skill_name -ne 'learning' -or -not $m.entry_point -or -not $m.files) { throw "Invalid manifest: $path" }
    $m
}

function Test-Package([string]$Dir, $Manifest) {
    <# Compare a skill directory with the manifest. Return a list of problems (empty = match). #>
    $problems = @()
    if (-not (Test-Path -LiteralPath $Dir -PathType Container)) { return @("missing directory: $Dir") }
    $root = (Resolve-Path -LiteralPath $Dir).Path.TrimEnd('\', '/')
    $expected = @{}
    foreach ($f in $Manifest.files) { $expected[$f.path] = $f.sha256 }
    if (-not $expected.ContainsKey($Manifest.entry_point)) { $problems += "manifest lacks entry point $($Manifest.entry_point)" }
    $actual = @{}
    foreach ($item in Get-ChildItem -LiteralPath $root -Recurse -File -Force) {
        $actual[$item.FullName.Substring($root.Length + 1).Replace('\', '/')] = $item.FullName
    }
    foreach ($p in $expected.Keys) {
        if (-not $actual.ContainsKey($p)) { $problems += "missing file: $p"; continue }
        $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $actual[$p]).Hash.ToLowerInvariant()
        if ($h -ne $expected[$p]) { $problems += "hash mismatch: $p" }
    }
    foreach ($p in $actual.Keys) {
        if (-not $expected.ContainsKey($p)) { $problems += "unexpected file (not in package, possible project state): $p" }
    }
    $problems
}

function Invoke-Fault([string]$Point) {
    if ($env:LEARNING_SKILL_TEST_FAULT -eq $Point) { throw "Injected test fault: $Point" }
}

function Install-Atomic([string]$SourceSkill, [string]$Target, $Manifest) {
    $claudeDir = Split-Path -Parent (Split-Path -Parent $Target)
    $work = Join-Path $claudeDir ".learning-install-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
    $stage = Join-Path $work 'stage'
    $backup = Join-Path $work 'backup'
    New-Item -ItemType Directory -Force -Path $work, (Split-Path -Parent $Target) | Out-Null
    $hadOld = Test-Path -LiteralPath $Target
    $movedOld = $false
    try {
        Copy-Item -LiteralPath $SourceSkill -Destination $stage -Recurse
        Invoke-Fault 'stage'
        $p = @(Test-Package $stage $Manifest)
        if ($p.Count) { throw "Staging verify failed: $($p -join '; ')" }
        if ($hadOld) { [IO.Directory]::Move($Target, $backup); $movedOld = $true }
        Invoke-Fault 'replace'
        [IO.Directory]::Move($stage, $Target)
        if ($env:LEARNING_SKILL_TEST_FAULT -eq 'verify') { Add-Content -LiteralPath (Join-Path $Target $Manifest.entry_point) -Value 'corrupt' }
        $p = @(Test-Package $Target $Manifest)
        if ($p.Count) { throw "Target verify failed: $($p -join '; ')" }
    }
    catch {
        $err = $_
        if ($movedOld) {
            if (Test-Path -LiteralPath $Target) { Remove-Item -LiteralPath $Target -Recurse -Force }
            [IO.Directory]::Move($backup, $Target)
            Write-Output 'ROLLBACK: previous install restored.'
        }
        elseif (-not $hadOld -and (Test-Path -LiteralPath $Target)) {
            Remove-Item -LiteralPath $Target -Recurse -Force
            Write-Output 'ROLLBACK: partial install removed.'
        }
        Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
        throw $err
    }
    Remove-Item -LiteralPath $work -Recurse -Force
}

$tmp = Join-Path ([IO.Path]::GetTempPath()) "learning-skill-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    $root = Get-SourceRoot $tmp
    $manifest = Read-Manifest $root
    $sourceSkill = (Resolve-Path -LiteralPath (Join-Path $root $SkillRel)).Path
    $problems = @(Test-Package $sourceSkill $manifest)
    if ($problems.Count) { throw "Source package verify failed. Nothing written.`n  $($problems -join "`n  ")" }
    Write-Output "Package: learning $($manifest.version) ($($manifest.files.Count) files) verified."

    $target = Join-Path (Get-TargetBase) $SkillRel
    $exists = Test-Path -LiteralPath $target
    if ($exists -and (Resolve-Path -LiteralPath $target).Path -eq $sourceSkill -and -not $VerifyOnly) {
        throw "Target is the source package itself: $target"
    }
    $same = $exists -and @(Test-Package $target $manifest).Count -eq 0

    if ($VerifyOnly) {
        if (-not $exists) { throw "FAIL: not installed at $target" }
        $p = @(Test-Package $target $manifest)
        if ($p.Count) { throw "FAIL: $target`n  $($p -join "`n  ")" }
        Write-Output "PASS: $target matches learning $($manifest.version)."
        return
    }
    if ($Update -and -not $exists) { throw "Update needs an existing install. Not found: $target" }
    if ($same) {
        Write-Output "ALREADY INSTALLED: learning $($manifest.version) at $target"
        return
    }
    if ($exists -and -not ($Update -or $Force)) {
        throw "A different learning skill exists at $target. Nothing written. Run update.ps1 (or install.ps1 -Force) to replace it."
    }
    Install-Atomic $sourceSkill $target $manifest
    $verb = if ($exists) { 'UPDATED' } else { 'INSTALLED' }
    Write-Output "${verb}: learning $($manifest.version) at $target"
    Write-Output 'Learning state (docs/learning/) and Personal Technical Library not touched.'
}
finally {
    Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
