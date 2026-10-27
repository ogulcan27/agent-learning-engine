<#
.SYNOPSIS
    Install, update or verify the Stay in the Loop skill (stay-in-the-loop).

.DESCRIPTION
    Quick install (asks for the scope):
      irm https://raw.githubusercontent.com/ogulcan27/stay-in-the-loop/v1.0.0/scripts/install.ps1 | iex

    Target (the only path this script owns):
      -Scope Project   <ProjectPath>/.claude/skills/stay-in-the-loop/   (default: current directory)
      -Scope Personal  <home>/.claude/skills/stay-in-the-loop/
      No -Scope        interactive menu: [1] Project, [2] Personal. Nothing is written before the choice.

    Source modes:
      ARCHIVE  -Archive <release zip>
      REMOTE   -Repository <owner/repo> and/or -Ref <tag-or-commit> (GitHub source archive)
      LOCAL    script run from a development repository (distribution/manifest.json next to scripts/)
      REMOTE   otherwise, with defaults Repository = ogulcan27/stay-in-the-loop, Ref = v1.0.0

    Flow: SOURCE -> MANIFEST/HASH VERIFY -> TARGET CHECK -> STAGE -> VERIFY
          -> OLD TARGET TO BACKUP -> STAGE TO TARGET -> VERIFY TARGET -> DELETE BACKUP.
    Any failure after the backup step restores the old target.
    The script never writes docs/learning/, the personal library, CLAUDE.md or other skills.

    The body runs in a child scope, so 'irm | iex' does not change the caller's session settings.
    Test-only hooks: $env:LEARNING_SKILL_TEST_FAULT = stage | replace | verify;
                     $env:LEARNING_SKILL_TEST_BASE_URL replaces https://github.com.
#>
[CmdletBinding()]
param(
    [string]$Scope,
    [string]$ProjectPath,
    [string]$Repository,
    [string]$Ref,
    [string]$Archive,
    [string]$BaseUrl,
    [switch]$Update,
    [switch]$Force,
    [switch]$VerifyOnly
)
& {
    $ErrorActionPreference = 'Stop'
    $ProgressPreference = 'SilentlyContinue'
    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $SkillRel = '.claude/skills/stay-in-the-loop'
    $DefaultRepository = 'ogulcan27/stay-in-the-loop'
    $DefaultRef = 'v1.0.0'
    if (-not $BaseUrl) { $BaseUrl = if ($env:LEARNING_SKILL_TEST_BASE_URL) { $env:LEARNING_SKILL_TEST_BASE_URL } else { 'https://github.com' } }

    function Read-Scope {
        <# Ask for the install scope until the answer is valid. Ctrl+C or end of input stops before any write. #>
        Write-Host ''
        Write-Host 'Stay in the Loop - choose where to install the stay-in-the-loop skill:'
        Write-Host ''
        Write-Host '  [1] Project'
        Write-Host "      Current project only: $((Get-Location).Path)"
        Write-Host '  [2] Personal'
        Write-Host '      All local Claude Code projects.'
        Write-Host ''
        while ($true) {
            $answer = Read-Host 'Select 1 or 2'
            if ($null -eq $answer) { throw 'No scope selected. Nothing written.' }
            switch -Regex ($answer.Trim()) {
                '^(1|project)$' { return 'Project' }
                '^(2|personal)$' { return 'Personal' }
            }
            Write-Host "Invalid choice '$answer'. Enter 1 (Project) or 2 (Personal)."
        }
    }

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
        <# Extract a zip. Return the directory that holds .claude/skills/stay-in-the-loop. #>
        [IO.Compression.ZipFile]::ExtractToDirectory($Zip, $Dest)
        if (Test-Path -LiteralPath (Join-Path $Dest $SkillRel)) { return $Dest }
        $dirs = @(Get-ChildItem -LiteralPath $Dest -Directory)
        if ($dirs.Count -eq 1 -and (Test-Path -LiteralPath (Join-Path $dirs[0].FullName $SkillRel))) { return $dirs[0].FullName }
        throw "Archive does not contain $SkillRel"
    }

    function Get-SourceRoot([string]$Work) {
        if ($Archive -and -not ($Repository -or $Ref)) {
            if (-not (Test-Path -LiteralPath $Archive -PathType Leaf)) { throw "Archive not found: $Archive" }
            return Expand-ToRoot (Resolve-Path -LiteralPath $Archive).Path (Join-Path $Work 'source')
        }
        $localRoot = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot }
        if (-not ($Repository -or $Ref) -and $localRoot -and (Test-Path -LiteralPath (Join-Path $localRoot 'distribution/manifest.json'))) {
            return $localRoot
        }
        $repo = if ($Repository) { $Repository } else { $DefaultRepository }
        $tag = if ($Ref) { $Ref } else { $DefaultRef }
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        $url = "$($BaseUrl.TrimEnd('/'))/$repo/archive/$tag.zip"
        $zip = Join-Path $Work 'source.zip'
        Write-Host "Download: $url"
        Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
        Expand-ToRoot $zip (Join-Path $Work 'source')
    }

    function Read-Manifest([string]$Root) {
        $path = Join-Path $Root 'distribution/manifest.json'
        if (-not (Test-Path -LiteralPath $path)) { throw "Manifest not found: $path" }
        $m = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
        if ($m.skill_name -ne 'stay-in-the-loop' -or -not $m.entry_point -or -not $m.files) { throw "Invalid manifest: $path" }
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
        $work = Join-Path $claudeDir ".stay-in-the-loop-install-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
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

    if (-not $Scope) { $Scope = Read-Scope }
    if ($Scope -notin 'Project', 'Personal') { throw "Invalid -Scope '$Scope'. Use Project or Personal." }

    $tmp = Join-Path ([IO.Path]::GetTempPath()) "stay-in-the-loop-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
    New-Item -ItemType Directory -Path $tmp | Out-Null
    try {
        $root = Get-SourceRoot $tmp
        $manifest = Read-Manifest $root
        $sourceSkill = (Resolve-Path -LiteralPath (Join-Path $root $SkillRel)).Path
        $problems = @(Test-Package $sourceSkill $manifest)
        if ($problems.Count) { throw "Source package verify failed. Nothing written.`n  $($problems -join "`n  ")" }
        Write-Output "Package: stay-in-the-loop $($manifest.version) ($($manifest.files.Count) files) verified."

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
            Write-Output "PASS: $target matches stay-in-the-loop $($manifest.version)."
            return
        }
        if ($Update -and -not $exists) { throw "Update needs an existing install. Not found: $target" }
        if ($same) {
            Write-Output "ALREADY INSTALLED: stay-in-the-loop $($manifest.version) at $target"
            return
        }
        if ($exists -and -not ($Update -or $Force)) {
            throw "A different stay-in-the-loop skill exists at $target. Nothing written. Run update.ps1 (or install.ps1 -Force) to replace it."
        }
        Install-Atomic $sourceSkill $target $manifest
        $verb = if ($exists) { 'UPDATED' } else { 'INSTALLED' }
        Write-Output "${verb}: stay-in-the-loop $($manifest.version) at $target"
        Write-Output 'Learning state (docs/learning/) and Personal Technical Library not touched.'
    }
    finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
