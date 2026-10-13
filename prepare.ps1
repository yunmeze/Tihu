# Windows PowerShell 5.1+, using built-in .NET libraries only.
param([string]$PackageRoot = $PSScriptRoot)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Assert-NoLinks([string]$Path) {
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        $item = $null
        try { $item = Get-Item -LiteralPath $current -Force -ErrorAction Stop }
        catch [System.Management.Automation.ItemNotFoundException] { }
        if ($null -ne $item) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Symlink/reparse-point path is not allowed: $current"
            }
        }
        $current = [IO.Path]::GetDirectoryName($current)
    }
}

function Get-SafePath([string]$Base, [string]$Relative) {
    if (-not $Relative -or $Relative.Contains('\') -or [IO.Path]::IsPathRooted($Relative)) { throw "Invalid relative path: $Relative" }
    foreach ($part in $Relative.Split('/')) {
        if (-not $part -or $part -eq '.' -or $part -eq '..' -or $part -match '[. ]$' -or $part -match '[\x00-\x1f<>:"|?*]' -or $part -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)') {
            throw "Unsafe or nonportable path: $Relative"
        }
    }
    $root = [IO.Path]::GetFullPath($Base).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    $target = [IO.Path]::GetFullPath([IO.Path]::Combine($Base, $Relative.Replace('/', [IO.Path]::DirectorySeparatorChar)))
    if (-not $target.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) { throw "Path escapes project: $Relative" }
    return $target
}

function Get-Sha256([string]$Path) {
    $hash = [Security.Cryptography.SHA256]::Create()
    $stream = [IO.File]::OpenRead($Path)
    try { return ([BitConverter]::ToString($hash.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $hash.Dispose() }
}

function Assert-File([string]$Path, $Record) {
    Assert-NoLinks $Path
    if (-not [IO.File]::Exists($Path)) { throw "Missing or nonregular file: $Path" }
    if ((Get-Item -LiteralPath $Path -Force).Length -ne [long]$Record.size -or (Get-Sha256 $Path) -cne $Record.sha256) { throw "Changed or corrupt file: $Path" }
}

function Assert-Destinations([string]$Project, $Files) {
    Assert-NoLinks $Project
    if ([IO.File]::Exists($Project)) { throw 'project exists but is not a directory' }
    foreach ($record in $Files) {
        $target = Get-SafePath $Project $record.path
        Assert-NoLinks $target
        $parent = [IO.Path]::GetDirectoryName($target)
        while ($parent -and $parent.Length -ge $Project.Length) {
            if ([IO.File]::Exists($parent)) { throw "A file blocks a destination directory: $parent" }
            $parent = [IO.Path]::GetDirectoryName($parent)
        }
        if ([IO.File]::Exists($target) -or [IO.Directory]::Exists($target)) {
            try { Assert-File $target $record }
            catch { throw "Will not overwrite an existing/modified file: $target. Use a fresh package folder, or back up and move that file yourself." }
        }
    }
}

$work = $null
try {
    if (-not $PackageRoot) { throw 'Package folder was not supplied' }
    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    if (-not [IO.Compression.ZipArchiveEntry].GetProperty('ExternalAttributes')) {
        throw 'This Windows unpacker needs .NET Framework 4.7.2 or newer. Keep your security settings; use prepare.py with an existing Python 3.8+ installation instead.'
    }
    $root = [IO.Path]::GetFullPath($PackageRoot)
    Assert-NoLinks $root
    $transport = Join-Path $root 'transport'
    $manifestPath = Join-Path $transport 'manifest.json'
    Assert-NoLinks $manifestPath
    $manifest = [IO.File]::ReadAllText($manifestPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    if ($manifest.version -ne 1 -or $manifest.archive_sha256 -cnotmatch '^[0-9a-f]{64}$' -or $manifest.archive_size -le 0) { throw 'Invalid manifest version, archive size, or SHA-256' }
    $files = @($manifest.files)
    $parts = @($manifest.parts)
    if ($files.Count -lt 1 -or $parts.Count -lt 1) { throw 'Invalid manifest file/part count' }
    $project = Join-Path $root 'project'
    $expected = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
    $caseNames = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($record in $files) {
        $null = Get-SafePath $project $record.path
        if (-not $caseNames.Add($record.path)) { throw "Duplicate/case-colliding manifest path: $($record.path)" }
        if ($record.mode -notin @('100644', '100755')) { throw 'Only regular files are supported' }
        $expected.Add($record.path, $record)
    }
    foreach ($record in $files) {
        $segments = $record.path.Split('/')
        for ($i = 1; $i -lt $segments.Length; $i++) {
            if ($caseNames.Contains(($segments[0..($i - 1)] -join '/'))) { throw 'File/directory collision in manifest' }
        }
    }
    [long]$totalSize = 0
    for ($i = 0; $i -lt $parts.Count; $i++) {
        $part = $parts[$i]
        if ($part.name -cne ('assets.part{0:D4}' -f $i)) { throw 'Missing, duplicate, or out-of-order chunk' }
        if ($part.size -le 0 -or $part.size -gt 196608 -or ($i -lt $parts.Count - 1 -and $part.size -ne 196608)) { throw 'Invalid chunk size' }
        $totalSize += [long]$part.size
    }
    foreach ($record in @($files) + @($parts)) {
        if ($record.size -lt 0 -or $record.sha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'Invalid size or SHA-256 in manifest' }
    }
    if ($totalSize -ne [long]$manifest.archive_size) { throw 'Archive size does not match chunks' }
    Assert-Destinations $project $files
    $work = Join-Path $root ('.pelican-prepare-' + [Guid]::NewGuid().ToString('N'))
    $null = [IO.Directory]::CreateDirectory($work)
    $staged = Join-Path $work 'project'
    $null = [IO.Directory]::CreateDirectory($staged)
    $archivePath = Join-Path $work 'assets.zip'
    Write-Host "Verifying and joining $($parts.Count) offline chunks..."
    $output = [IO.File]::Open($archivePath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        foreach ($part in $parts) {
            $sourcePath = Join-Path $transport $part.name
            Assert-File $sourcePath $part
            $source = [IO.File]::OpenRead($sourcePath)
            try { $source.CopyTo($output) } finally { $source.Dispose() }
        }
    } finally { $output.Dispose() }
    Assert-File $archivePath ([pscustomobject]@{size = $manifest.archive_size; sha256 = $manifest.archive_sha256})
    Write-Host 'Archive verified. Extracting to a temporary folder...'
    $zip = [IO.Compression.ZipFile]::OpenRead($archivePath)
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    try {
        if ($zip.Entries.Count -ne $files.Count) { throw 'ZIP file count differs from manifest' }
        foreach ($entry in $zip.Entries) {
            $target = Get-SafePath $staged $entry.FullName
            if (-not $expected.ContainsKey($entry.FullName) -or -not $seen.Add($entry.FullName) -or -not $entry.Name) { throw "Unexpected/duplicate ZIP entry: $($entry.FullName)" }
            $kind = ($entry.ExternalAttributes -shr 16) -band 61440
            if ($kind -ne 0 -and $kind -ne 32768) { throw "Nonregular ZIP entry: $($entry.FullName)" }
            $record = $expected[$entry.FullName]
            if ($entry.Length -ne [long]$record.size) { throw 'Unexpected ZIP entry size' }
            $null = [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($target))
            $input = $entry.Open()
            try {
                $output = [IO.File]::Open($target, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
                try { $input.CopyTo($output) } finally { $output.Dispose() }
            } finally { $input.Dispose() }
            Assert-File $target $record
        }
    } finally { $zip.Dispose() }
    if ($seen.Count -ne $files.Count) { throw 'ZIP is incomplete' }
    Assert-Destinations $project $files
    Write-Host "All $($files.Count) extracted hashes verified. Preparing project/..."
    foreach ($record in $files) {
        $target = Get-SafePath $project $record.path
        Assert-NoLinks $target
        if ([IO.File]::Exists($target)) { Assert-File $target $record; continue }
        $parent = [IO.Path]::GetDirectoryName($target)
        $null = [IO.Directory]::CreateDirectory($parent)
        Assert-NoLinks $parent
        # Copy(..., false) is exclusive: it never replaces an existing file.
        [IO.File]::Copy((Get-SafePath $staged $record.path), $target, $false)
        Assert-File $target $record
    }
    foreach ($record in $files) { Assert-File (Get-SafePath $project $record.path) $record }
    Write-Host "SUCCESS: all $($files.Count) project files match the checkpoint."
    Write-Host 'Open project/project.godot with Godot 4.6.3 Standard, wait for import, then press F5.'
} catch {
    Write-Host ('PREPARATION FAILED: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    if ($work -and [IO.Directory]::Exists($work)) { [IO.Directory]::Delete($work, $true) }
}
