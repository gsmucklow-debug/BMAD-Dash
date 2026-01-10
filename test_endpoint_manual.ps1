# Manual Test Script for Test Evidence API Endpoint
# Usage: .\test_endpoint_manual.ps1

$baseUrl = "http://localhost:5000"
$projectRoot = "F:\BMAD Dash"

Write-Host "`n=== Testing Test Evidence API Endpoint ===" -ForegroundColor Cyan
Write-Host "Base URL: $baseUrl" -ForegroundColor Gray
Write-Host "Project Root: $projectRoot`n" -ForegroundColor Gray

# Test 1: Missing project_root parameter (should return 400)
Write-Host "Test 1: Missing project_root parameter" -ForegroundColor Yellow
Write-Host "Expected: 400 Bad Request`n" -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/test-evidence/2.3" -Method GET -ErrorAction Stop
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)`n" -ForegroundColor White
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    $errorContent = $_.ErrorDetails.Message | ConvertFrom-Json
    Write-Host "Status: $statusCode" -ForegroundColor Red
    Write-Host "Error: $($errorContent.error)" -ForegroundColor Red
    Write-Host "Message: $($errorContent.message)" -ForegroundColor Yellow
    Write-Host "Details: $($errorContent.details)`n" -ForegroundColor Gray
}

# Test 2: Valid story with project_root (should return 200)
Write-Host "Test 2: Valid story (2.3) with project_root" -ForegroundColor Yellow
Write-Host "Expected: 200 OK with test evidence`n" -ForegroundColor Gray
try {
    $uri = "$baseUrl/api/test-evidence/2.3?project_root=$([System.Web.HttpUtility]::UrlEncode($projectRoot))"
    $response = Invoke-RestMethod -Uri $uri -Method GET -ErrorAction Stop
    Write-Host "Status: 200 OK" -ForegroundColor Green
    Write-Host "Story ID: $($response.story_id)" -ForegroundColor White
    Write-Host "Status: $($response.status)" -ForegroundColor $(if ($response.status -eq 'green') { 'Green' } else { 'Yellow' })
    Write-Host "Total Tests: $($response.total_tests)" -ForegroundColor White
    Write-Host "Passing: $($response.pass_count)" -ForegroundColor Green
    Write-Host "Failing: $($response.fail_count)" -ForegroundColor $(if ($response.fail_count -gt 0) { 'Red' } else { 'Green' })
    Write-Host "Last Run: $($response.last_run_time)`n" -ForegroundColor Gray
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Host "Status: $statusCode" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        $errorContent = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Error: $($errorContent.error)" -ForegroundColor Red
        Write-Host "Message: $($errorContent.message)`n" -ForegroundColor Yellow
    } else {
        Write-Host "Error: $($_.Exception.Message)`n" -ForegroundColor Red
    }
}

# Test 3: Non-existent story (should return 404)
Write-Host "Test 3: Non-existent story (99.99)" -ForegroundColor Yellow
Write-Host "Expected: 404 Not Found`n" -ForegroundColor Gray
try {
    $uri = "$baseUrl/api/test-evidence/99.99?project_root=$([System.Web.HttpUtility]::UrlEncode($projectRoot))"
    $response = Invoke-RestMethod -Uri $uri -Method GET -ErrorAction Stop
    Write-Host "Status: 200 OK (unexpected!)" -ForegroundColor Red
    Write-Host "Response: $($response | ConvertTo-Json)`n" -ForegroundColor White
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 404) {
        Write-Host "Status: 404 Not Found ✓" -ForegroundColor Green
        $errorContent = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Error: $($errorContent.error)" -ForegroundColor Red
        Write-Host "Message: $($errorContent.message)" -ForegroundColor Yellow
        Write-Host "Details: $($errorContent.details)`n" -ForegroundColor Gray
    } else {
        Write-Host "Status: $statusCode (unexpected)" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)`n" -ForegroundColor Red
    }
}

# Test 4: Invalid story ID format (should return 404)
Write-Host "Test 4: Invalid story ID format (invalid-story)" -ForegroundColor Yellow
Write-Host "Expected: 404 Not Found`n" -ForegroundColor Gray
try {
    $uri = "$baseUrl/api/test-evidence/invalid-story?project_root=$([System.Web.HttpUtility]::UrlEncode($projectRoot))"
    $response = Invoke-RestMethod -Uri $uri -Method GET -ErrorAction Stop
    Write-Host "Status: 200 OK (unexpected!)" -ForegroundColor Red
    Write-Host "Response: $($response | ConvertTo-Json)`n" -ForegroundColor White
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 404) {
        Write-Host "Status: 404 Not Found ✓" -ForegroundColor Green
        $errorContent = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Error: $($errorContent.error)" -ForegroundColor Red
        Write-Host "Message: $($errorContent.message)`n" -ForegroundColor Yellow
    } else {
        Write-Host "Status: $statusCode (unexpected)" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)`n" -ForegroundColor Red
    }
}

# Test 5: Another valid story (1.3) if it exists
Write-Host "Test 5: Another story (1.3) with project_root" -ForegroundColor Yellow
Write-Host "Expected: 200 OK or 404 if story doesn't exist`n" -ForegroundColor Gray
try {
    $uri = "$baseUrl/api/test-evidence/1.3?project_root=$([System.Web.HttpUtility]::UrlEncode($projectRoot))"
    $response = Invoke-RestMethod -Uri $uri -Method GET -ErrorAction Stop
    Write-Host "Status: 200 OK" -ForegroundColor Green
    Write-Host "Story ID: $($response.story_id)" -ForegroundColor White
    Write-Host "Status: $($response.status)" -ForegroundColor $(if ($response.status -eq 'green') { 'Green' } elseif ($response.status -eq 'yellow') { 'Yellow' } else { 'Red' })
    Write-Host "Total Tests: $($response.total_tests)" -ForegroundColor White
    Write-Host "Passing: $($response.pass_count)" -ForegroundColor Green
    Write-Host "Failing: $($response.fail_count)" -ForegroundColor $(if ($response.fail_count -gt 0) { 'Red' } else { 'Green' })
    Write-Host "Test Files: $($response.test_files.Count) found`n" -ForegroundColor Gray
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 404) {
        Write-Host "Status: 404 Not Found" -ForegroundColor Yellow
        Write-Host "Story 1.3 does not exist`n" -ForegroundColor Gray
    } else {
        Write-Host "Status: $statusCode" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)`n" -ForegroundColor Red
    }
}

Write-Host "`n=== Testing Complete ===" -ForegroundColor Cyan
Write-Host "`nTo test manually in a browser or with curl:" -ForegroundColor Yellow
Write-Host "1. Missing param: http://localhost:5000/api/test-evidence/2.3" -ForegroundColor Gray
Write-Host "2. Valid story: http://localhost:5000/api/test-evidence/2.3?project_root=F:\BMAD Dash" -ForegroundColor Gray
Write-Host "3. Non-existent: http://localhost:5000/api/test-evidence/99.99?project_root=F:\BMAD Dash" -ForegroundColor Gray
Write-Host "`nNote: URL encode spaces in project_root for browser testing" -ForegroundColor Gray
