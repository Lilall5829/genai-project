# build.ps1 - 转换自 Makefile
param([string]$Task = "help")

switch ($Task) {
    "compose-up" {
        docker compose -f infra/docker-compose.yml up -d --build
    }
    "compose-down" {
        docker compose -f infra/docker-compose.yml down
    }
    # "smoke" {
    #     powershell -ExecutionPolicy Bypass -File eval/smoke.ps1
    # }
    "help" {
        Write-Host "Available tasks:"
        Write-Host "  compose-up   - Start Docker Compose services"
        Write-Host "  compose-down - Stop Docker Compose services"
        # Write-Host "  smoke        - Run smoke tests"
    }
    default {
        Write-Host "Unknown task: $Task. Run '.\build.ps1 help' for available tasks."
    }
}