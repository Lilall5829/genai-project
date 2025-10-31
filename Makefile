.PHONY: compose-up compose-down smoke

compose-up:
    docker compose -f infra/docker-compose.yml up -d --build

compose-down:
    docker compose -f infra/docker-compose.yml down

smoke:
    powershell -ExecutionPolicy Bypass -File eval/smoke.ps1