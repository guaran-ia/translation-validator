<# 
    start_batch_all.ps1
    ====================
    Inicia los 3 servicios de anotación (POS, Features, Relations) 
    para un mismo lote en puertos diferentes.
    
    Uso:
        .\start_batch_all.ps1 -Batch 1
        .\start_batch_all.ps1 -Batch 5 -BasePort 8080
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateRange(1, 60)]
    [int]$Batch,
    
    [Parameter(Mandatory=$false)]
    [int]$BasePort = 8080
)

# Configurar encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# Obtener directorio del script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Puertos para cada servicio
$PortPOS = $BasePort
$PortFeatures = $BasePort + 1
$PortRelations = $BasePort + 2

# Nombres de datasets
$BatchStr = $Batch.ToString("D2")
$DatasetPOS = "guarani_pos_batch_$BatchStr"
$DatasetFeatures = "guarani_features_batch_$BatchStr"
$DatasetRelations = "guarani_relations_batch_$BatchStr"

# Path al recipe
$RecipePath = Join-Path $ScriptDir "recipes\guarani_batch.py"

# Verificar que existe el archivo de lotes
$BatchFile = Join-Path $ScriptDir "data\batches\batch_$($Batch.ToString('D3')).jsonl"
if (-not (Test-Path $BatchFile)) {
    Write-Host ""
    Write-Host "ERROR: No existe el archivo de lote: $BatchFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Ejecute primero el generador de lotes:" -ForegroundColor Yellow
    Write-Host "  python scripts\generate_batches.py --input data\export\original_translations.jsonl --output data\batches" -ForegroundColor White
    Write-Host ""
    exit 1
}

$SentenceCount = (Get-Content $BatchFile | Measure-Object -Line).Lines

# Mostrar banner
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "     PRODIGY - Sistema de Anotacion por Lotes" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  LOTE:       $Batch (de 60)" -ForegroundColor Yellow
Write-Host "  ORACIONES:  $SentenceCount" -ForegroundColor Yellow
Write-Host ""
Write-Host "  SERVICIOS:" -ForegroundColor Green
Write-Host "  +-----------+----------------------------+------------------+" -ForegroundColor Gray
Write-Host "  | TIPO      | DATASET                    | URL              |" -ForegroundColor Gray
Write-Host "  +-----------+----------------------------+------------------+" -ForegroundColor Gray
Write-Host "  | POS       | $DatasetPOS      | http://localhost:$PortPOS |" -ForegroundColor Blue
Write-Host "  | Features  | $DatasetFeatures | http://localhost:$PortFeatures |" -ForegroundColor Green
Write-Host "  | Relations | $DatasetRelations | http://localhost:$PortRelations |" -ForegroundColor Yellow
Write-Host "  +-----------+----------------------------+------------------+" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Matar procesos de Prodigy anteriores en estos puertos
Write-Host "Limpiando procesos anteriores..." -ForegroundColor Gray
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    try {
        $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
        if ($cmdLine -match "prodigy" -or $cmdLine -match "guarani") {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}
Start-Sleep -Seconds 1

# Iniciar POS
Write-Host "Iniciando POS en puerto $PortPOS..." -ForegroundColor Blue
$posCMD = "cd `"$ScriptDir`"; `$env:PRODIGY_PORT=$PortPOS; `$env:PRODIGY_HOST='0.0.0.0'; python -m prodigy guarani-batch $DatasetPOS -t pos -l $Batch -F `"$RecipePath`""
Start-Process powershell -ArgumentList "-NoExit", "-Command", $posCMD -WindowStyle Normal

Start-Sleep -Seconds 2

# Iniciar Features
Write-Host "Iniciando Features en puerto $PortFeatures..." -ForegroundColor Green
$featuresCMD = "cd `"$ScriptDir`"; `$env:PRODIGY_PORT=$PortFeatures; `$env:PRODIGY_HOST='0.0.0.0'; python -m prodigy guarani-batch $DatasetFeatures -t features -l $Batch -F `"$RecipePath`""
Start-Process powershell -ArgumentList "-NoExit", "-Command", $featuresCMD -WindowStyle Normal

Start-Sleep -Seconds 2

# Iniciar Relations
Write-Host "Iniciando Relations en puerto $PortRelations..." -ForegroundColor Yellow
$relationsCMD = "cd `"$ScriptDir`"; `$env:PRODIGY_PORT=$PortRelations; `$env:PRODIGY_HOST='0.0.0.0'; python -m prodigy guarani-batch $DatasetRelations -t relations -l $Batch -F `"$RecipePath`""
Start-Process powershell -ArgumentList "-NoExit", "-Command", $relationsCMD -WindowStyle Normal

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  ¡3 SERVICIOS INICIADOS!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Abre en tu navegador:" -ForegroundColor White
Write-Host ""
Write-Host "    POS:       http://localhost:$PortPOS" -ForegroundColor Blue
Write-Host "    Features:  http://localhost:$PortFeatures" -ForegroundColor Green  
Write-Host "    Relations: http://localhost:$PortRelations" -ForegroundColor Yellow
Write-Host ""
Write-Host "  O abre la UI unificada: batch_selector.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Para detener: Cierra las ventanas de PowerShell" -ForegroundColor Gray
Write-Host ""
