# =============================================================================
# Script para iniciar Prodigy con recipe de Relaciones Sintacticas + Proxy JWT
# =============================================================================
# Anotacion de dependencias sintacticas y relaciones semanticas
# Tokenizacion a nivel de PALABRA
#
# Uso:
#   .\start_prodigy_relations_secure.ps1
#   .\start_prodigy_relations_secure.ps1 -Group "relations"
#   .\start_prodigy_relations_secure.ps1 -Group "pos-tags" -Limit 50
#
# Grupos UD disponibles:
#   relations    - Relaciones sintacticas (SUJETO, OBJETO, RAIZ, etc.)
#   pos-tags     - Categorias gramaticales (Verbo, Sustantivo, etc.)
#   features     - Rasgos morfologicos
#   morfemas     - Raiz, Prefijo, Sufijo
# =============================================================================

param(
    [string]$Dataset = "guarani_relations_secure",
    [string]$Source = "",
    [int]$Port = 8082,
    [int]$Limit = 100,
    [string]$Group = "relations"
)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  PRODIGY RELATIONS SECURE" -ForegroundColor Yellow
Write-Host "  Anotacion de Dependencias Sintacticas con JWT" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  COMO FUNCIONA:" -ForegroundColor Green
Write-Host "    1. Carga las traducciones del corpus" -ForegroundColor White
Write-Host "    2. Tokeniza a nivel de PALABRA" -ForegroundColor White
Write-Host "    3. Puedes dibujar arcos entre palabras" -ForegroundColor White
Write-Host "    4. Cada arco tiene una etiqueta de relacion" -ForegroundColor White
Write-Host ""
Write-Host "  CONTROLES:" -ForegroundColor Cyan
Write-Host "    - Click en palabra 1, luego click en palabra 2 = crear arco" -ForegroundColor White
Write-Host "    - Click en arco = eliminar relacion" -ForegroundColor White
Write-Host "    - Ctrl+Shift+C = Ver contexto (oracion anterior/siguiente)" -ForegroundColor White
Write-Host ""
Write-Host "  CONFIGURACION:" -ForegroundColor Cyan
Write-Host "    Dataset:   $Dataset" -ForegroundColor White
Write-Host "    Puerto:    $Port (proxy seguro JWT)" -ForegroundColor White
Write-Host "    Limite:    $Limit oraciones" -ForegroundColor White
Write-Host "    Grupo:     $Group" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ETIQUETAS DE RELACIONES:" -ForegroundColor Cyan
Write-Host "    RAIZ (Verbo Principal)  - Nucleo de la oracion" -ForegroundColor Yellow
Write-Host "    SUJETO                  - Sujeto nominal" -ForegroundColor Yellow
Write-Host "    OBJETO DIRECTO          - Objeto directo" -ForegroundColor Yellow
Write-Host "    OBJETO INDIRECTO        - Objeto indirecto" -ForegroundColor Yellow
Write-Host "    COMPLEMENTO OBLICUO     - Nominal oblicuo" -ForegroundColor Yellow
Write-Host "    MODIFICADOR ADVERBIAL   - Modificador adverbial" -ForegroundColor Yellow
Write-Host "    MODIFICADOR NOMINAL     - Modificador nominal" -ForegroundColor Yellow
Write-Host "    ... y mas (ver GUIA_ANOTACION.md)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  ACCESO:" -ForegroundColor Green
Write-Host "    1. Login en http://localhost:5173" -ForegroundColor White
Write-Host "    2. Dashboard -> Prodigy" -ForegroundColor White
Write-Host "    3. Click en 'Abrir Prodigy'" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Construir argumentos para el script Python
$args = @(
    "-d", $Dataset,
    "-g", $Group,
    "-l", $Limit,
    "-p", $Port
)

if ($Source -ne "") {
    $args += @("-s", $Source)
}

# Ejecutar el script Python que maneja el proxy JWT
$scriptPath = Join-Path $PSScriptRoot "start_prodigy_relations_secure.py"

Write-Host "Ejecutando: python $scriptPath $($args -join ' ')" -ForegroundColor DarkGray
Write-Host ""

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Ejecutar
python $scriptPath @args
