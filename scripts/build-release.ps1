<#
.SYNOPSIS
    Build distribution/manifest.json and the release package in dist/.

.DESCRIPTION
    Development repository script. Reads VERSION and .claude/skills/stay-in-the-loop/.
    Writes:
      distribution/manifest.json
      dist/stay-in-the-loop-v<VERSION>.zip
      dist/SHA256SUMS.txt
    The ZIP holds only .claude/skills/stay-in-the-loop/ and distribution/manifest.json.
    Entry order and timestamps are fixed, so the ZIP is deterministic.
#>
[CmdletBinding()]
param(
    [string]$RepoRoot,
    [string]$OutDir
)
$ErrorActionPreference = 'Stop'
if (-not $RepoRoot) { $RepoRoot = Split-Path -Parent $PSScriptRoot }
Add-Type -AssemblyName System.IO.Compression

$skillRel = '.claude/skills/stay-in-the-loop'
$skillDir = Join-Path $RepoRoot $skillRel
$version = (Get-Content -Raw (Join-Path $RepoRoot 'VERSION')).Trim()
if (-not $OutDir) { $OutDir = Join-Path $RepoRoot 'dist' }

function Get-Sha256([string]$Path) {
    (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Get-SkillFiles([string]$Dir) {
    $root = (Resolve-Path -LiteralPath $Dir).Path.TrimEnd('\', '/')
    [string[]]$rel = Get-ChildItem -LiteralPath $root -Recurse -File -Force |
        ForEach-Object { $_.FullName.Substring($root.Length + 1).Replace('\', '/') }
    [Array]::Sort($rel, [StringComparer]::Ordinal)
    $rel
}

$files = @(Get-SkillFiles $skillDir | ForEach-Object {
    [ordered]@{ path = $_; sha256 = (Get-Sha256 (Join-Path $skillDir $_)) }
})
$manifest = [ordered]@{
    version     = $version
    skill_name  = 'stay-in-the-loop'
    entry_point = 'SKILL.md'
    package_root = $skillRel
    files       = $files
}
$manifestDir = Join-Path $RepoRoot 'distribution'
New-Item -ItemType Directory -Force -Path $manifestDir | Out-Null
$manifestPath = Join-Path $manifestDir 'manifest.json'
$json = ($manifest | ConvertTo-Json -Depth 5) -replace "`r`n", "`n"
[IO.File]::WriteAllText($manifestPath, $json + "`n", (New-Object Text.UTF8Encoding $false))

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$zipName = "stay-in-the-loop-v$version.zip"
$zipPath = Join-Path $OutDir $zipName
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }

$entries = @($files | ForEach-Object { @{ name = "$skillRel/$($_.path)"; source = (Join-Path $skillDir $_.path) } })
$entries += @{ name = 'distribution/manifest.json'; source = $manifestPath }
$stamp = [DateTimeOffset]::new(2000, 1, 1, 0, 0, 0, [TimeSpan]::Zero)
$stream = [IO.File]::Open($zipPath, 'CreateNew')
$zip = New-Object IO.Compression.ZipArchive($stream, [IO.Compression.ZipArchiveMode]::Create)
foreach ($e in $entries) {
    $entry = $zip.CreateEntry($e.name, [IO.Compression.CompressionLevel]::Optimal)
    $entry.LastWriteTime = $stamp
    $out = $entry.Open()
    $bytes = [IO.File]::ReadAllBytes($e.source)
    $out.Write($bytes, 0, $bytes.Length)
    $out.Dispose()
}
$zip.Dispose()
$stream.Dispose()

$sums = "$(Get-Sha256 $zipPath)  $zipName`n"
[IO.File]::WriteAllText((Join-Path $OutDir 'SHA256SUMS.txt'), $sums, (New-Object Text.UTF8Encoding $false))

Write-Output "Manifest: $($files.Count) files, version $version"
Write-Output "Package:  $zipPath"
Write-Output "SHA256:   $($sums.Trim())"
