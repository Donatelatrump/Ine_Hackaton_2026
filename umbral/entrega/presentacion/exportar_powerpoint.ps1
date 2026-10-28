$ErrorActionPreference = 'Stop'
$pptReview = New-Object -ComObject PowerPoint.Application
$pptFile = Join-Path $PSScriptRoot 'Umbral_presentacion.pptx'
$pptDeck = $pptReview.Presentations.Open($pptFile, -1, 0, 0)
try {
    $pptDeck.SaveAs((Join-Path $PSScriptRoot 'Umbral_presentacion.pdf'), 32)
} finally {
    $pptDeck.Close()
}
