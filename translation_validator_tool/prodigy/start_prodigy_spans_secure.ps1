# Script para iniciar Prodigy SPANS con proxy seguro (JWT)
# Mismo patrón que start_prodigy_openai_secure.ps1 pero sin OpenAI
# Proxy en puerto 8082, Prodigy interno en 8080

param(
    [Parameter()]
    [string]$Dataset = "guarani_spans_secure",
    
    [Parameter()]
    [string]$Source = "",
    
    [Parameter()]
    [int]$Port = 8082,
    
    [Parameter()]
    [int]$Limit = 100,
    
    [Parameter()]
    [ValidateSet(
        "",
        "pos-tags",
        "features",
        "morfemas",
        "features-persona-numero",
        "features-caso",
        "features-tam",
        "features-relacional",
        "features-nominalizadores",
        "features-otros"
    )]
    [string]$Group = "",
    
    [Parameter()]
    [switch]$WordLevel,
    
    [Parameter()]
    [switch]$ListGroups
)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  PRODIGY SPANS SECURE - Anotacion Morfologica del Guarani" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($ListGroups) {
    Write-Host "  GRUPOS DE ETIQUETAS DISPONIBLES:" -ForegroundColor Green
    Write-Host ""
    Write-Host "    pos-tags              POS Tags (VERB, NOUN, PRON, etc.)" -ForegroundColor White
    Write-Host "    features              Todos los features morfologicos" -ForegroundColor White
    Write-Host "    morfemas              Raiz, Prefijo, Sufijo" -ForegroundColor White
    Write-Host ""
    Write-Host "  SUBGRUPOS DE FEATURES:" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "    features-persona-numero    Persona, Numero, Clusividad" -ForegroundColor Gray
    Write-Host "    features-caso              Casos (Ablativo, Locativo, etc.)" -ForegroundColor Gray
    Write-Host "    features-tam               Tiempo, Aspecto, Modo" -ForegroundColor Gray
    Write-Host "    features-relacional        Prefijos relacionales" -ForegroundColor Gray
    Write-Host "    features-nominalizadores   Nominalizadores" -ForegroundColor Gray
    Write-Host "    features-otros             Otros features" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  EJEMPLO:" -ForegroundColor Green
    Write-Host ""
    Write-Host "    .\start_prodigy_spans_secure.ps1 -Group pos-tags" -ForegroundColor Cyan
    Write-Host "    .\start_prodigy_spans_secure.ps1 -Group features-tam -Limit 50" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}

Write-Host "  GRUPOS DE ETIQUETAS:" -ForegroundColor Green
Write-Host ""
Write-Host "    pos-tags              POS Tags (VERB, NOUN, PRON, ADV...)" -ForegroundColor White
Write-Host "    features              Todos los features morfologicos" -ForegroundColor White
Write-Host "    morfemas              Raiz, Prefijo, Sufijo" -ForegroundColor White
Write-Host ""
Write-Host "    features-persona-numero, features-caso, features-tam," -ForegroundColor Gray
Write-Host "    features-relacional, features-nominalizadores, features-otros" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION SELECCIONADA:" -ForegroundColor Magenta
Write-Host ""
Write-Host "    Dataset:   $Dataset" -ForegroundColor White
if ($Source -ne "") {
    Write-Host "    Source:    $Source" -ForegroundColor White
} else {
    Write-Host "    Source:    (auto: translations.csv)" -ForegroundColor Gray
}
Write-Host "    Limite:    $Limit oraciones" -ForegroundColor White
if ($Group -ne "") {
    Write-Host "    Grupo:     $Group" -ForegroundColor Yellow
} else {
    Write-Host "    Grupo:     (todas las etiquetas)" -ForegroundColor Gray
}
if ($WordLevel) {
    Write-Host "    Modo:      Por PALABRA" -ForegroundColor White
} else {
    Write-Host "    Modo:      Por CARACTER (default)" -ForegroundColor Yellow
}
Write-Host "    Puerto:    $Port (proxy JWT)" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  ACCESO:" -ForegroundColor Green
Write-Host ""
Write-Host "    1. Login en http://localhost:5173" -ForegroundColor White
Write-Host "    2. Dashboard -> Prodigy" -ForegroundColor White
Write-Host "    3. Click en 'Abrir Prodigy'" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Construir comando
$cmd = "python start_prodigy_spans_secure.py -d `"$Dataset`" -p $Port -l $Limit"

if ($Source -ne "") {
    $cmd = "$cmd -s `"$Source`""
}

if ($Group -ne "") {
    $cmd = "$cmd -g `"$Group`""
}

if ($WordLevel) {
    $cmd = "$cmd --word-level"
}

Write-Host "Ejecutando: $cmd" -ForegroundColor DarkGray
Write-Host ""

Invoke-Expression $cmd
