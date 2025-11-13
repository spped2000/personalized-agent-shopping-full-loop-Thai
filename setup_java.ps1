# Auto-detect and configure Java for the project
# This script finds the best Java version (21+) and sets it for the current session

Write-Host "Searching for Java installations..." -ForegroundColor Cyan

# Search common Java installation directories
$javaSearchPaths = @(
    "C:\Program Files\Eclipse Adoptium",
    "C:\Program Files\Java",
    "C:\Program Files\OpenJDK",
    "C:\Program Files (x86)\Eclipse Adoptium",
    "C:\Program Files (x86)\Java",
    "C:\Program Files (x86)\OpenJDK"
)

$javaInstallations = @()

foreach ($searchPath in $javaSearchPaths) {
    if (Test-Path $searchPath) {
        $jdkDirs = Get-ChildItem -Path $searchPath -Filter "jdk*" -Directory -ErrorAction SilentlyContinue
        foreach ($jdkDir in $jdkDirs) {
            $javaExe = Join-Path $jdkDir.FullName "bin\java.exe"
            if (Test-Path $javaExe) {
                # Extract version number from directory name
                if ($jdkDir.Name -match "jdk-?(\d+)") {
                    $version = [int]$matches[1]
                    $javaInstallations += [PSCustomObject]@{
                        Path = $jdkDir.FullName
                        Version = $version
                        Name = $jdkDir.Name
                    }
                }
            }
        }
    }
}

if ($javaInstallations.Count -eq 0) {
    Write-Host "ERROR: No Java installation found!" -ForegroundColor Red
    Write-Host "Please install Java 21 or higher from https://adoptium.net/" -ForegroundColor Yellow
    exit 1
}

# Sort by version (highest first) and pick the best one (21+)
$bestJava = $javaInstallations | Where-Object { $_.Version -ge 21 } | Sort-Object -Property Version -Descending | Select-Object -First 1

if ($null -eq $bestJava) {
    Write-Host "ERROR: Found Java installations, but none are version 21 or higher!" -ForegroundColor Red
    Write-Host "Found versions:" -ForegroundColor Yellow
    foreach ($java in $javaInstallations) {
        Write-Host "  - Java $($java.Version): $($java.Path)" -ForegroundColor Yellow
    }
    Write-Host "`nPlease install Java 21 or higher from https://adoptium.net/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found Java $($bestJava.Version): $($bestJava.Path)" -ForegroundColor Green

# Set environment variables for current session
$env:JAVA_HOME = $bestJava.Path
$env:PATH = "$($bestJava.Path)\bin;$env:PATH"

Write-Host "`nJava configured successfully!" -ForegroundColor Green
Write-Host "JAVA_HOME = $env:JAVA_HOME" -ForegroundColor Cyan

# Verify
Write-Host "`nVerifying Java version..." -ForegroundColor Cyan
& java -version

Write-Host "`n" -NoNewline
Write-Host "You can now run your Python scripts. For example:" -ForegroundColor Green
Write-Host "  cd personalized_shopping\shared_libraries\search_engine" -ForegroundColor Cyan
Write-Host "  uv run python convert_product_file_format.py" -ForegroundColor Cyan
