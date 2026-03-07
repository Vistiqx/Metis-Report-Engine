# Test-MetisReport.ps1
# PowerShell script to test Metis Report Engine PDF generation
# This script uses the updated API that returns PDF files directly

param(
    [string]$ServerUrl = "http://192.168.239.197:8000",
    [string]$ReportPath = "meta_ai_glasses_risk_assessment.canonical.json",
    [string]$OutputPath = "report_output.pdf"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Metis Report Engine - PDF Generation Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if report file exists
if (-not (Test-Path $ReportPath)) {
    Write-Host "ERROR: Report file not found: $ReportPath" -ForegroundColor Red
    Write-Host "Please ensure the canonical JSON report file exists in the current directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "Loading report from: $ReportPath" -ForegroundColor Green

# Read and parse the report JSON
try {
    $reportJson = Get-Content $ReportPath -Raw | ConvertFrom-Json
    Write-Host "Report loaded successfully" -ForegroundColor Green
    Write-Host "  Report ID: $($reportJson.report.id)" -ForegroundColor Gray
    Write-Host "  Title: $($reportJson.report.title)" -ForegroundColor Gray
    Write-Host "  Findings: $($reportJson.findings.Count)" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: Failed to parse report JSON: $_" -ForegroundColor Red
    exit 1
}

# Method 1: Direct PDF download (recommended)
Write-Host ""
Write-Host "Method 1: Direct PDF download (default mode)" -ForegroundColor Cyan
Write-Host "Sending POST request to: $ServerUrl/render-pdf" -ForegroundColor Gray

try {
    $body = @{
        report = $reportJson
        template = "professional"
    } | ConvertTo-Json -Depth 10
    
    $response = Invoke-WebRequest -Uri "$ServerUrl/render-pdf" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -OutFile $OutputPath
    
    Write-Host "SUCCESS! PDF downloaded to: $OutputPath" -ForegroundColor Green
    
    # Verify file was created
    if (Test-Path $OutputPath) {
        $fileInfo = Get-Item $OutputPath
        Write-Host "  File size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
        Write-Host "  File path: $($fileInfo.FullName)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "ERROR: Failed to generate/download PDF: $_" -ForegroundColor Red
    
    # Try to get more error details
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $responseBody = $reader.ReadToEnd()
        Write-Host "Server response: $responseBody" -ForegroundColor Yellow
    }
}

# Method 2: Metadata mode (alternative approach)
Write-Host ""
Write-Host "Method 2: Metadata mode with artifact download" -ForegroundColor Cyan
Write-Host "This method returns a JSON response with download URL" -ForegroundColor Gray

try {
    $body = @{
        report = $reportJson
        template = "professional"
    } | ConvertTo-Json -Depth 10
    
    $response = Invoke-WebRequest -Uri "$ServerUrl/render-pdf?return_type=metadata" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
    
    $metadata = $response.Content | ConvertFrom-Json
    
    if ($metadata.status -eq "success") {
        Write-Host "Metadata received:" -ForegroundColor Green
        Write-Host "  Artifact URL: $($metadata.artifact_url)" -ForegroundColor Gray
        Write-Host "  Filename: $($metadata.filename)" -ForegroundColor Gray
        Write-Host "  Size: $([math]::Round($metadata.pdf_size / 1KB, 2)) KB" -ForegroundColor Gray
        
        # Download the artifact
        $artifactPath = "report_output_metadata_mode.pdf"
        $artifactResponse = Invoke-WebRequest -Uri "$ServerUrl$($metadata.artifact_url)" -OutFile $artifactPath
        
        Write-Host "SUCCESS! Artifact downloaded to: $artifactPath" -ForegroundColor Green
        
        if (Test-Path $artifactPath) {
            $fileInfo = Get-Item $artifactPath
            Write-Host "  File size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
        }
    } else {
        Write-Host "ERROR: PDF generation failed: $($metadata.message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "ERROR: Method 2 failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
