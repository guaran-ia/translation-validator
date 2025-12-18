<#
    start_prodigy_manager.ps1
    =========================
    Inicia el Prodigy Manager - Sistema unificado de anotación con JWT
    
    Características:
    - Proxy seguro en puerto 8085
    - Valida tokens JWT del backend
    - Permite elegir tipo de anotación desde la UI
    - Gestiona múltiples tipos: Batch, Spans, OpenAI, Relations
    
    Uso:
        .\start_prodigy_manager.ps1
        .\start_prodigy_manager.ps1 -Port 8085
#>

param(
    [int]$Port = 8085
)

# Configurar encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# Obtener directorio del script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  PRODIGY MANAGER" -ForegroundColor Yellow
Write-Host "  Sistema Unificado de Anotacion con JWT" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  CARACTERISTICAS:" -ForegroundColor Green
Write-Host "    - Proxy seguro con validacion JWT" -ForegroundColor White
Write-Host "    - Multiples tipos de anotacion desde una UI" -ForegroundColor White
Write-Host "    - Gestion de lotes (Batch POS/Features/Relations)" -ForegroundColor White
Write-Host "    - Anotacion manual (Spans)" -ForegroundColor White
Write-Host "    - Pre-anotacion con OpenAI" -ForegroundColor White
Write-Host "    - Relaciones sintacticas" -ForegroundColor White
Write-Host ""
Write-Host "  CONFIGURACION:" -ForegroundColor Cyan
Write-Host "    Puerto Proxy:  $Port" -ForegroundColor White
Write-Host ""
Write-Host "  ACCESO:" -ForegroundColor Green
Write-Host "    1. Login en http://localhost:5173" -ForegroundColor White
Write-Host "    2. Dashboard -> Prodigy" -ForegroundColor White
Write-Host "    3. Seleccionar tipo de anotacion" -ForegroundColor White
Write-Host "    4. Click en 'Iniciar Servicio'" -ForegroundColor White
Write-Host ""
Write-Host "  PUERTOS DE SERVICIOS:" -ForegroundColor Cyan
Write-Host "    POS        -> 8080" -ForegroundColor White
Write-Host "    Features   -> 8081" -ForegroundColor White
Write-Host "    Relations  -> 8082" -ForegroundColor White
Write-Host ""
Write-Host "  API ENDPOINTS:" -ForegroundColor Cyan
Write-Host "    GET  /api/status           - Estado del sistema" -ForegroundColor Gray
Write-Host "    GET  /api/services         - Servicios en ejecucion" -ForegroundColor Gray
Write-Host "    GET  /api/types            - Tipos disponibles" -ForegroundColor Gray
Write-Host "    POST /api/start-prodigy    - Iniciar servicio" -ForegroundColor Gray
Write-Host "    POST /api/stop-prodigy/{s} - Detener servicio" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Ejecutar
python prodigy_manager.py --port $Port
