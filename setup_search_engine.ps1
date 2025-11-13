# Complete setup script for search engine
# This script:
# 1. Configures Java
# 2. Creates resource directories
# 3. Converts product data
# 4. Builds search index

Write-Host "=== Search Engine Setup ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Setup Java
Write-Host "[1/4] Configuring Java..." -ForegroundColor Yellow
. .\setup_java.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Java setup failed. Please fix Java installation first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Create directories
Write-Host "[2/4] Creating resource directories..." -ForegroundColor Yellow
$searchEngineDir = "personalized_shopping\shared_libraries\search_engine"
Push-Location $searchEngineDir

if (!(Test-Path "resources_100")) {
    New-Item -ItemType Directory -Name "resources_100" -Force | Out-Null
    Write-Host "Created resources_100/" -ForegroundColor Green
}
if (!(Test-Path "resources_1k")) {
    New-Item -ItemType Directory -Name "resources_1k" -Force | Out-Null
    Write-Host "Created resources_1k/" -ForegroundColor Green
}

Write-Host ""

# Step 3: Convert product data
Write-Host "[3/4] Converting product data to search format..." -ForegroundColor Yellow
Write-Host "(This may take a minute...)" -ForegroundColor Gray

uv run python convert_product_file_format.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Product conversion failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""

# Step 4: Build search index
Write-Host "[4/4] Building search index..." -ForegroundColor Yellow
Write-Host "(This will take 2-3 seconds...)" -ForegroundColor Gray

uv run python -m pyserini.index.lucene `
    --collection JsonCollection `
    --input resources_1k `
    --index indexes_1k `
    --generator DefaultLuceneDocumentGenerator `
    --threads 1 `
    --storePositions --storeDocvectors --storeRaw

if ($LASTEXITCODE -ne 0) {
    Write-Host "Index creation failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run the agent with:" -ForegroundColor Cyan
Write-Host "  uv run adk web" -ForegroundColor White
Write-Host ""
