# ============================================================================
# Stop Batch Auto-Advance System
# ============================================================================
# Detiene todos los servicios del sistema de auto-avance de batches.
# ============================================================================

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  DETENIENDO BATCH AUTO-ADVANCE SYSTEM" -ForegroundColor Cyan  
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Detener servicios vía API
$services = @("pos", "features", "relations")

foreach ($service in $services) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8085/api/stop-prodigy/$service" `
            -Method Post `
            -Headers @{Authorization="Bearer internal-monitor"} `
            -TimeoutSec 5 `
            -ErrorAction SilentlyContinue
        
        if ($response.success) {
            Write-Host "  [OK] Servicio $($service.ToUpper()) detenido" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [--] Servicio $service no estaba corriendo" -ForegroundColor Yellow
    }
}

# Buscar y matar procesos de Python relacionados
$processes = Get-Process -Name "python*" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -match "prodigy|batch_monitor" }

if ($processes) {
    foreach ($proc in $processes) {
        try {
            Stop-Process -Id $proc.Id -Force
            Write-Host "  [OK] Proceso $($proc.Id) detenido" -ForegroundColor Green
        } catch {
            Write-Host "  [FAIL] No se pudo detener proceso $($proc.Id)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  [--] No hay procesos de Prodigy corriendo" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "  Sistema detenido." -ForegroundColor Green
Write-Host ""
