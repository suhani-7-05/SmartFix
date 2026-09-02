#!/bin/bash

services=(
  "orchestrator:8000"
  "rag:8001"
  "equipment:8002"
  "safety:8003"
  "history:8004"
  "spare_parts:8005"
  "tickets:8006"
  "llm:8007"
)

for service in "${services[@]}"; do
    IFS=: read -r name port <<< "$service"
    uvicorn "services.$name.main:app" --port "$port" --reload &
done

wait
