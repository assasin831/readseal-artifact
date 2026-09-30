param()
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
    if ($LASTEXITCODE -ne 0) { throw 'First LaTeX pass failed' }
    & bibtex main
    if ($LASTEXITCODE -ne 0) { throw 'Bibliography build failed' }
    foreach ($pass in 1..2) {
        & pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
        if ($LASTEXITCODE -ne 0) { throw 'LaTeX pass failed' }
    }
    Write-Output 'Built main.pdf'
} finally {
    Pop-Location
}
