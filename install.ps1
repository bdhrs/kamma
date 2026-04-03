$ErrorActionPreference = 'Stop'

$RepoZip = "https://github.com/bdhrs/kamma/archive/refs/heads/main.zip"
$InstallDir = Join-Path $HOME "kamma"

# Check for uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv is not installed. uv is required to run kamma."
    $answer = Read-Host "Install it now? [y/N]"
    if ($answer -match '^[Yy]$') {
        irm https://astral.sh/uv/install.ps1 | iex
        $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
    } else {
        Write-Host "Aborted."
        exit 1
    }
}

# Download and extract
Write-Host "Downloading kamma..."
$TmpDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid())
New-Item -ItemType Directory -Path $TmpDir | Out-Null

try {
    $ZipPath = Join-Path $TmpDir "kamma.zip"
    Invoke-WebRequest -Uri $RepoZip -OutFile $ZipPath
    Expand-Archive -Path $ZipPath -DestinationPath $TmpDir -Force

    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
    }
    Move-Item -Path (Join-Path $TmpDir "kamma-main") -Destination $InstallDir
} finally {
    Remove-Item -Recurse -Force $TmpDir -ErrorAction SilentlyContinue
}

# Run sync
Write-Host "Syncing..."
Set-Location $InstallDir
uv run python scripts/sync.py
