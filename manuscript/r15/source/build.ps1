param(
    [string]$Python = "python",
    [string]$LibreOffice = "C:/Program Files/LibreOffice/program/soffice.com",
    [switch]$RegenerateFigures
)
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    if ($RegenerateFigures) {
        & node scripts/make_diagrams_pptx.js
        if ($LASTEXITCODE -ne 0) { throw "Diagram generation failed" }
        & node scripts/make_charts_pptx.js
        if ($LASTEXITCODE -ne 0) { throw "Chart generation failed" }
        $names = "fig1_overview", "fig2_trace", "fig3_boundaries", "fig5_delivery", "fig6_slots", "fig7_mixed"
        $inputs = $names | ForEach-Object { Join-Path $PSScriptRoot "figures/$_.pptx" }
        $export = 'pdf:impress_pdf_Export:{"UseLosslessCompression":{"type":"boolean","value":"true"},"ReduceImageResolution":{"type":"boolean","value":"false"},"EmbedStandardFonts":{"type":"boolean","value":"true"}}'
        $profile = [System.Uri]::new((Join-Path $PSScriptRoot ".lo-build-profile")).AbsoluteUri
        & $LibreOffice "-env:UserInstallation=$profile" --headless --convert-to $export --outdir figures @inputs
        if ($LASTEXITCODE -ne 0) { throw "Figure PDF export failed" }
    }
    & pdflatex -interaction=nonstopmode -halt-on-error main.tex
    if ($LASTEXITCODE -ne 0) { throw "First LaTeX pass failed" }
    & bibtex main
    if ($LASTEXITCODE -ne 0) { throw "Bibliography build failed" }
    1..2 | ForEach-Object {
        & pdflatex -interaction=nonstopmode -halt-on-error main.tex
        if ($LASTEXITCODE -ne 0) { throw "LaTeX pass failed" }
    }
    & $Python scripts/finalize_pdf.py
    if ($LASTEXITCODE -ne 0) { throw "PDF verification failed" }
} finally {
    Pop-Location
}
