# ============================================================================
# Start Batch Auto-Advance System
# ============================================================================
# Inicia el sistema completo de batches con auto-avance:
# 1. Prodigy Manager (proxy y gestión de servicios)
# 2. Batch Monitor (detección de completado y auto-avance)
# 3. Los 3 servicios de Prodigy (POS, Features, Relations)
#
# Uso:
#   .\start_batch_auto.ps1                    # Batch 1
#   .\start_batch_auto.ps1 -Batch 5           # Empezar desde batch 5
#   .\start_batch_auto.ps1 -Interval 30       # Chequear cada 30 segundos
# ============================================================================

param(
    [int]$Batch = 1,
    [int]$Interval = 60,
    [switch]$NoMonitor,
    [switch]$Help
)

# Colores
$colors = @{
    Header = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 64) -ForegroundColor $colors.Header
    Write-Host "  $Text" -ForegroundColor $colors.Header
    Write-Host ("=" * 64) -ForegroundColor $colors.Header
    Write-Host ""
}

function Write-Step {
    param([string]$Number, [string]$Text, [string]$Status = "...")
    $icon = switch ($Status) {
        "OK" { "[OK]"; $color = $colors.Success }
        "SKIP" { "[SKIP]"; $color = $colors.Warning }
        "FAIL" { "[FAIL]"; $color = $colors.Error }
        default { "[...]"; $color = $colors.Info }
    }
    Write-Host "  $icon " -NoNewline -ForegroundColor $color
    Write-Host "$Number. $Text"
}

function Show-Help {
    Write-Header "BATCH AUTO-ADVANCE SYSTEM - Ayuda"
    Write-Host @"
  Este script inicia el sistema completo de anotación con auto-avance.
  
  PARÁMETROS:
    -Batch <N>       Número de batch inicial (default: 1)
    -Interval <N>    Intervalo de chequeo en segundos (default: 60)
    -NoMonitor       No iniciar el batch monitor
    -Help            Mostrar esta ayuda

  EJEMPLOS:
    .\start_batch_auto.ps1
    .\start_batch_auto.ps1 -Batch 5
    .\start_batch_auto.ps1 -Interval 30
    
  COMPONENTES:
    1. Prodigy Manager    Puerto 8085 - Proxy y gestión
    2. Batch Monitor      Detecta completado y auto-avanza
    3. POS Service        Puerto 8080 - Etiquetado POS
    4. Features Service   Puerto 8081 - Características morfológicas
    5. Relations Service  Puerto 8082 - Relaciones sintácticas

  VALIDADORES:
    El sistema avanza cuando TODOS los validadores asignados completan.
    Configurar en .env: VALIDATORS_POS, VALIDATORS_FEATURES, VALIDATORS_RELATIONS

"@
}

if ($Help) {
    Show-Help
    exit 0
}

# Directorio base
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Header "BATCH AUTO-ADVANCE SYSTEM"

Write-Host "  Configuración:" -ForegroundColor $colors.Info
Write-Host "    Batch inicial:        $Batch"
Write-Host "    Intervalo chequeo:    ${Interval}s"
Write-Host "    Batch Monitor:        $(if ($NoMonitor) { 'Deshabilitado' } else { 'Habilitado' })"
Write-Host ""

# Cargar variables de entorno
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]*)\s*=\s*(.*)\s*$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
    Write-Step "0" "Variables de entorno cargadas" "OK"
}

# Verificar Python
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Step "1" "Python no encontrado" "FAIL"
    exit 1
}
Write-Step "1" "Python encontrado: $($pythonCmd)" "OK"

# Verificar Prodigy
try {
    & $pythonCmd -m prodigy --help | Out-Null
    Write-Step "2" "Prodigy disponible" "OK"
} catch {
    Write-Step "2" "Prodigy no instalado" "FAIL"
    exit 1
}

# Iniciar Prodigy Manager
Write-Host ""
Write-Host "  Iniciando servicios..." -ForegroundColor $colors.Info
Write-Host ""

$managerJob = Start-Job -ScriptBlock {
    param($dir, $python)
    Set-Location $dir
    & $python prodigy_manager.py --port 8085
} -ArgumentList $scriptDir, $pythonCmd

Start-Sleep -Seconds 3

if ($managerJob.State -eq "Running") {
    Write-Step "3" "Prodigy Manager iniciado (puerto 8085)" "OK"
} else {
    Write-Step "3" "Error iniciando Prodigy Manager" "FAIL"
    Receive-Job $managerJob
    exit 1
}

# Esperar a que el manager esté listo
Write-Host "  Esperando que el manager este listo..." -ForegroundColor $colors.Info
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8085/api/status" -Method Get -TimeoutSec 3 -ErrorAction Stop
        if ($response -ne $null) {
            $ready = $true
            break
        }
    } catch {
        # Ignorar errores y seguir intentando
    }
    Start-Sleep -Seconds 1
    if ($i % 10 -eq 0 -and $i -gt 0) {
        Write-Host "    ... esperando ($i segundos)" -ForegroundColor $colors.Warning
    }
}

if (-not $ready) {
    Write-Step "4" "Manager no responde" "FAIL"
    exit 1
}
Write-Step "4" "Manager listo" "OK"

# Iniciar los 3 servicios de Prodigy
$services = @("pos", "features", "relations")
$ports = @{pos=8080; features=8081; relations=8082}

# Intentar leer el estado actual de batches por servicio desde data/batch_monitor_state.json
$stateFile = Join-Path $scriptDir "data\batch_monitor_state.json"
$serviceBatches = @{}
foreach ($s in $services) { $serviceBatches[$s] = $Batch }

if (Test-Path $stateFile) {
    try {
        $json = Get-Content $stateFile -Raw | ConvertFrom-Json
        if ($json -and $json.current_batch) {
            foreach ($s in $services) {
                if ($json.current_batch.PSObject.Properties.Name -contains $s) {
                    $val = $json.current_batch.$s
                    if ($val -is [int]) { $serviceBatches[$s] = $val }
                }
            }
            Write-Step "5a" "Cargado batch actual desde data/batch_monitor_state.json" "OK"
        } else {
            Write-Step "5a" "Archivo de estado no contiene 'current_batch' - usando parámetro -Batch" "SKIP"
        }
    } catch {
        Write-Step "5a" "Error leyendo archivo de estado: $_ - usando parámetro -Batch" "WARNING"
    }
} else {
    Write-Step "5a" "No se encontró data/batch_monitor_state.json - usando parámetro -Batch" "SKIP"
}

foreach ($service in $services) {
    $port = $ports[$service]
    $serviceBatch = $serviceBatches[$service]
    
    # Intentar iniciar vía API
    try {
        $body = @{
            recipe = "batch"
            annotation_type = $service
            batch_number = $serviceBatch
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8085/api/start-prodigy" `
            -Method Post `
            -Body $body `
            -ContentType "application/json" `
            -Headers @{Authorization="Bearer internal-monitor"} `
            -TimeoutSec 30
        
        if ($response.success) {
            Write-Step "5" "Servicio $($service.ToUpper()) iniciado (puerto $port, batch $serviceBatch)" "OK"
        } else {
            Write-Step "5" "Error iniciando $service" "FAIL"
        }
    } catch {
        Write-Step "5" "Error conectando para $service : $_" "FAIL"
    }
    
    Start-Sleep -Seconds 2
}

# Iniciar Batch Monitor
$monitorJob = $null
if (-not $NoMonitor) {
    Write-Host ""
    Write-Step "6" "Batch Monitor se iniciara en primer plano (intervalo: ${Interval}s, validadores: $Validators)" "OK"
}

# Resumen final
Write-Header "SISTEMA INICIADO"

Write-Host @"
  ACCESO:
    1. UI Principal:     http://localhost:5173
    2. Prodigy Manager:  http://localhost:8085
    3. POS Directo:      http://localhost:8080
    4. Features Directo: http://localhost:8081
    5. Relations Directo:http://localhost:8082

  SESIONES DE ANOTACIÓN:
    - POS: $($env:VALIDATORS_POS)
    - Features: $($env:VALIDATORS_FEATURES)
    - Relations: $($env:VALIDATORS_RELATIONS)
    - Acceder: http://localhost:8085/?session=<nombre>

  AUTO-AVANCE:
    - El monitor chequea cada ${Interval}s
    - Cuando los validadores asignados completen 50 frases
    - Se inicia automáticamente el siguiente batch

  PARA DETENER:
    - Presiona Ctrl+C
    - O ejecuta: .\stop_batch_auto.ps1

"@

# Ejecutar batch monitor en primer plano para ver siempre el output
try {
    if (-not $NoMonitor) {
        Write-Host "  Iniciando Batch Monitor..." -ForegroundColor $colors.Info
        Write-Host ""
        
        # Ejecutar en primer plano - asi siempre se ve el output
        & $pythonCmd batch_monitor.py --interval $Interval
    } else {
        Write-Host "  Presiona Ctrl+C para detener..." -ForegroundColor $colors.Warning
        Write-Host ""
        
        # Sin monitor, solo esperar
        while ($true) {
            if ($managerJob.State -ne "Running") {
                Write-Host ""
                Write-Host "  [!] Prodigy Manager detenido" -ForegroundColor $colors.Error
                Receive-Job $managerJob
                break
            }
            Start-Sleep -Seconds 5
        }
    }
} finally {
    # Cleanup
    Write-Host ""
    Write-Host "  Deteniendo servicios..." -ForegroundColor $colors.Warning
    
    # Detener servicios de Prodigy vía API
    foreach ($service in $services) {
        try {
            Invoke-RestMethod -Uri "http://localhost:8085/api/stop-prodigy/$service" `
                -Method Post `
                -Headers @{Authorization="Bearer internal-monitor"} `
                -TimeoutSec 5 `
                -ErrorAction SilentlyContinue | Out-Null
        } catch {}
    }
    
    Stop-Job $managerJob -ErrorAction SilentlyContinue
    Remove-Job $managerJob -Force -ErrorAction SilentlyContinue
    
    Write-Host "  Sistema detenido." -ForegroundColor $colors.Success
}
