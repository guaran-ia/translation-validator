<# 
    start_prodigy_batch.ps1
    =======================
    Script para iniciar Prodigy con un lote específico.
    
    Uso:
        .\start_prodigy_batch.ps1 -Type pos -Batch 1
        .\start_prodigy_batch.ps1 -Type features -Batch 5 -Port 8081
        .\start_prodigy_batch.ps1 -Type relations -Batch 10 -Port 8082
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("pos", "features", "relations")]
    [string]$Type,
    
    [Parameter(Mandatory=$true)]
    [ValidateRange(1, 60)]
    [int]$Batch,
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 8080,
    
    [Parameter(Mandatory=$false)]
    [string]$Host = "0.0.0.0"
)

# Configurar encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# Obtener directorio del script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Configurar variables de entorno de Prodigy
$env:PRODIGY_HOST = $Host
$env:PRODIGY_PORT = $Port
$env:PRODIGY_LOGGING = "verbose"

# Nombre del dataset
$BatchStr = $Batch.ToString("D2")
$DatasetName = "guarani_${Type}_batch_${BatchStr}"

# Path al recipe
$RecipePath = Join-Path $ScriptDir "recipes\guarani_batch.py"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PRODIGY - Guarani Annotation Tool" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Tipo:     $Type" -ForegroundColor Yellow
Write-Host "  Lote:     $Batch (50 oraciones)" -ForegroundColor Yellow
Write-Host "  Dataset:  $DatasetName" -ForegroundColor Yellow
Write-Host "  Puerto:   $Port" -ForegroundColor Yellow
Write-Host ""
Write-Host "  URL: http://localhost:$Port" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que existe el archivo de lotes
$BatchFile = Join-Path $ScriptDir "data\batches\batch_${BatchStr}.jsonl"
if (-not (Test-Path $BatchFile)) {
    Write-Host "ERROR: No existe el archivo de lote: $BatchFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ejecute primero el generador de lotes:" -ForegroundColor Yellow
    Write-Host "  python scripts\generate_batches.py --source data\export\original_translations.jsonl --output data\batches" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "Archivo de lote: $BatchFile" -ForegroundColor Gray
Write-Host "Oraciones en lote: $((Get-Content $BatchFile | Measure-Object -Line).Lines)" -ForegroundColor Gray
Write-Host ""

# Iniciar Prodigy
Write-Host "Iniciando Prodigy..." -ForegroundColor Green
Write-Host ""

try {
    python -m prodigy guarani-batch $DatasetName -t $Type -l $Batch -F $RecipePath
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
