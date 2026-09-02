# SmartFix Windows PowerShell Service Launcher

Write-Host "Starting SmartFix Microservices on Windows..." -ForegroundColor Cyan

$services = @(
    @{ Name = "orchestrator"; Port = 8000 },
    @{ Name = "rag";          Port = 8001 },
    @{ Name = "equipment";    Port = 8002 },
    @{ Name = "safety";       Port = 8003 },
    @{ Name = "history";      Port = 8004 },
    @{ Name = "spare_parts";  Port = 8005 },
    @{ Name = "tickets";      Port = 8006 },
    @{ Name = "llm";          Port = 8007 }
)

$processes = @()

foreach ($svc in $services) {
    Write-Host "-> Launching $($svc.Name) on port $($svc.Port)..." -ForegroundColor Green
    $p = Start-Process -FilePath "python" -ArgumentList "-m uvicorn services.$($svc.Name).main:app --port $($svc.Port) --reload" -PassThru
    $processes += $p
}

Write-Host "`nAll 8 Microservices are running in the background." -ForegroundColor Yellow
Write-Host "Orchestrator URL: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "To stop all services later, run: Stop-Process -Name python" -ForegroundColor Gray
