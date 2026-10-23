$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
if (Test-Path '.venv/Scripts/python.exe') {
    $pythonExe = (Resolve-Path '.venv/Scripts/python.exe').Path
} else {
    $pythonExe = 'py'
}
if ($pythonExe -eq 'py') {
    & py -3.13 -m pytest backend/tests -q
} else {
    & $pythonExe -m pytest backend/tests -q
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (Get-Command node -ErrorAction SilentlyContinue) {
    node --check frontend/js/api.js
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    node --check frontend/js/app.js
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    node --check frontend/js/charts.js
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    node --test frontend/tests/api.test.cjs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host 'Frontend tests NOT RUN: install Node.js 22+ (CI runs these tests automatically).'
}
