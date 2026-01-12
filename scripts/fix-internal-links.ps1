# PowerShell script to fix internal links in docs to use absolute paths with /docs/ prefix

$ErrorActionPreference = "Stop"

function Fix-InternalLinks {
    param([string]$filePath)
    
    $content = Get-Content $filePath -Raw -Encoding UTF8
    $originalContent = $content
    $filename = Split-Path $filePath -Leaf
    
    # Calculate the relative depth of the file from docs/ folder
    $relativePath = $filePath -replace [regex]::Escape("e:\Project\primerlab-genomic\docs\"), ""
    $depth = ($relativePath.Split('\').Length - 1)
    
    # Pattern 1: ](guides/ -> ](/docs/guides/
    $content = $content -replace '\]\(guides/', '](/docs/guides/'
    
    # Pattern 2: ](reference/ -> ](/docs/reference/
    $content = $content -replace '\]\(reference/', '](/docs/reference/'
    
    # Pattern 3: ](concepts/ -> ](/docs/concepts/
    $content = $content -replace '\]\(concepts/', '](/docs/concepts/'
    
    # Pattern 4: ](tutorials/ -> ](/docs/tutorials/
    $content = $content -replace '\]\(tutorials/', '](/docs/tutorials/'
    
    # Pattern 5: ](troubleshooting) -> ](/docs/troubleshooting)
    $content = $content -replace '\]\(troubleshooting\)', '](/docs/troubleshooting)'
    
    # Pattern 6: ](getting-started) -> ](/docs/getting-started)
    $content = $content -replace '\]\(getting-started\)', '](/docs/getting-started)'
    
    # Pattern 7: ](changelog) -> ](/docs/changelog)
    $content = $content -replace '\]\(changelog\)', '](/docs/changelog)'
    
    # Pattern 8: ](../ relative paths -> convert to absolute
    # For ../guides/ -> /docs/guides/
    $content = $content -replace '\]\(\.\./guides/', '](/docs/guides/'
    
    # For ../reference/ -> /docs/reference/
    $content = $content -replace '\]\(\.\./reference/', '](/docs/reference/'
    
    # For ../concepts/ -> /docs/concepts/
    $content = $content -replace '\]\(\.\./concepts/', '](/docs/concepts/'
    
    # For ../tutorials/ -> /docs/tutorials/
    $content = $content -replace '\]\(\.\./tutorials/', '](/docs/tutorials/'
    
    # For ../features/ -> /docs/concepts/features/
    $content = $content -replace '\]\(\.\./features/', '](/docs/concepts/features/'
    
    # For ../../features/ -> /docs/concepts/features/
    $content = $content -replace '\]\(\.\./\.\./features/', '](/docs/concepts/features/'
    
    # For ../troubleshooting) -> /docs/troubleshooting)
    $content = $content -replace '\]\(\.\./troubleshooting\)', '](/docs/troubleshooting)'
    
    # For ../getting-started) -> /docs/getting-started)
    $content = $content -replace '\]\(\.\./getting-started\)', '](/docs/getting-started)'
    
    # For ../configuration/ -> /docs/reference/ (configuration was moved to reference)
    $content = $content -replace '\]\(\.\./configuration/', '](/docs/reference/'
    
    # For ../cli/ -> /docs/reference/cli/
    $content = $content -replace '\]\(\.\./cli/', '](/docs/reference/cli/'
    
    # For ../workflows/ -> (these don't exist, link to guides)
    $content = $content -replace '\]\(\.\./workflows/pcr\)', '](/docs/guides/pcr-design)'
    
    # Fix broken README links
    $content = $content -replace '\]\([^)]*README\)', '](#)'
    
    # Fix ../../examples/ links to GitHub
    $content = $content -replace '\]\(\.\./\.\./examples/[^)]*\)', '](https://github.com/engkinandatama/primerlab-genomic/tree/main/examples)'
    
    if ($content -ne $originalContent) {
        Set-Content -Path $filePath -Value $content -Encoding UTF8 -NoNewline
        Write-Host "  Fixed: $filename"
        return $true
    } else {
        Write-Host "  No changes: $filename"
        return $false
    }
}

$fixedCount = 0

# Process all markdown files in docs/
Get-ChildItem "docs" -Recurse -Filter "*.md" | ForEach-Object {
    $result = Fix-InternalLinks $_.FullName
    if ($result) { $fixedCount++ }
}

Write-Host "`nDone! Fixed $fixedCount files."
