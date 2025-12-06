# =============================================================================
# Script SEGURO para iniciar Prodigy con OpenAI + Proxy JWT
# =============================================================================
# Igual que start_prodigy_spans_secure pero con OpenAI pre-anotando automático
#
# El flujo es:
# 1. Carga las traducciones originales (translations.csv)
# 2. OpenAI analiza cada oración y genera spans automáticamente
# 3. El usuario ve los spans ya marcados y puede corregir
#
# Uso:
#   .\start_prodigy_openai_secure.ps1
#   .\start_prodigy_openai_secure.ps1 -Model "gpt-4o" -Limit 50
#   .\start_prodigy_openai_secure.ps1 -Group "morfemas-basicos"
#
# Grupos disponibles:
#   morfemas-basicos, categorias, persona-numero, tam,
#   caso-relacional, voz-polaridad, nominalizadores, otros-features
# =============================================================================

param(
    [string]$Dataset = "guarani_openai_secure",
    [string]$Source = "",
    [string]$Model = "gpt-4o-mini",
    [int]$Port = 8082,
    [int]$Limit = 100,
    [switch]$NoCache,
    [string]$Group = ""
)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  PRODIGY + OpenAI SECURE" -ForegroundColor Yellow
Write-Host "  Anotacion Morfologica AUTOMATICA con IA" -ForegroundColor Yellow  
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  COMO FUNCIONA:" -ForegroundColor Green
Write-Host "    1. Carga tus traducciones originales (translations.csv)" -ForegroundColor White
Write-Host "    2. OpenAI analiza cada oracion en Guarani" -ForegroundColor White
Write-Host "    3. Te muestra los morfemas YA MARCADOS automaticamente" -ForegroundColor White
Write-Host "    4. Tu solo corriges lo que este mal!" -ForegroundColor White
Write-Host ""
Write-Host "  NUEVA FUNCIONALIDAD:" -ForegroundColor Cyan
Write-Host "    Boton 'Ver Contexto' - Muestra oracion anterior y siguiente" -ForegroundColor Yellow
Write-Host "    Atajo: Alt+C para abrir el popup de contexto" -ForegroundColor Yellow
Write-Host ""
Write-Host "  CONFIGURACION:" -ForegroundColor Cyan
Write-Host "    Dataset:   $Dataset" -ForegroundColor White
Write-Host "    Modelo:    $Model" -ForegroundColor White
Write-Host "    Limite:    $Limit oraciones" -ForegroundColor White
Write-Host "    Puerto:    $Port (proxy seguro)" -ForegroundColor White
Write-Host "    Cache:     $(if ($NoCache) { 'Desactivado' } else { 'Activado' })" -ForegroundColor White
if ($Group -ne "") {
    Write-Host "    Grupo:     $Group" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "  GRUPOS UD PRINCIPALES:" -ForegroundColor Cyan
Write-Host "    pos-tags           - Categorias gramaticales (UPOS)" -ForegroundColor Yellow
Write-Host "    features           - Rasgos morfologicos" -ForegroundColor Yellow
Write-Host "    morfemas           - Raiz, Prefijo, Sufijo" -ForegroundColor Yellow
Write-Host ""
Write-Host "  SUBGRUPOS DE FEATURES:" -ForegroundColor Cyan
Write-Host "    features-persona-numero  - Persona, Numero, Clusividad" -ForegroundColor DarkGray
Write-Host "    features-caso            - Ablativo, Locativo, etc." -ForegroundColor DarkGray
Write-Host "    features-tam             - Tiempo, Aspecto, Modo" -ForegroundColor DarkGray
Write-Host "    features-relacional      - Prefijos relacionales" -ForegroundColor DarkGray
Write-Host "    features-nominalizadores - Nominalizadores" -ForegroundColor DarkGray
Write-Host "    features-otros           - Otros features" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  ACCESO:" -ForegroundColor Green
Write-Host "    1. Login en http://localhost:5173" -ForegroundColor White
Write-Host "    2. Dashboard -> Prodigy" -ForegroundColor White
Write-Host "    3. Click en 'Abrir Prodigy'" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

# Construir argumentos
$args = @(
    "-d", $Dataset,
    "-m", $Model,
    "-p", $Port,
    "-l", $Limit
)

if ($Source -ne "") {
    $args += @("-s", $Source)
}

if ($NoCache) {
    $args += "--no-cache"
}

if ($Group -ne "") {
    $args += @("-g", $Group)
}

# Ejecutar
$scriptPath = Join-Path $PSScriptRoot "start_prodigy_openai_secure.py"
Write-Host "Ejecutando: python $scriptPath $($args -join ' ')" -ForegroundColor DarkGray
Write-Host ""

python $scriptPath @args
