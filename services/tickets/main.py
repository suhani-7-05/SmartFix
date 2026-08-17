"""
SmartFix Service Ticket Service — Exercise 4

Creates and tracks service tickets when equipment troubleshooting requires technician dispatch.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="SmartFix Service Ticket Service", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TICKETS_DATABASE: dict[str, dict[str, Any]] = {}


class CreateTicketRequest(BaseModel):
    equipment_id: str = Field(..., description="Target Equipment ID")
    issue_summary: str = Field(..., description="Brief summary of unresolved issue or safety blockage")
    priority: str = Field(default="HIGH", description="Ticket priority (LOW, MEDIUM, HIGH, CRITICAL)")
    safety_decision: str = Field(default="ALLOWED", description="Associated safety engine decision")
    assigned_team: str = Field(default="DevOps On-Call Field Techs", description="Assigned team")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "smartfix-ticket-service", "total_tickets": len(TICKETS_DATABASE)}


@app.get("/tickets")
async def list_tickets():
    return list(TICKETS_DATABASE.values())


@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    t_id = ticket_id.upper()
    if t_id not in TICKETS_DATABASE:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return TICKETS_DATABASE[t_id]


@app.post("/tickets/create")
async def create_ticket(body: CreateTicketRequest) -> dict[str, Any]:
    ticket_num = len(TICKETS_DATABASE) + 1001
    ticket_id = f"TKT-{ticket_num}"

    ticket_record = {
        "ticket_id": ticket_id,
        "equipment_id": body.equipment_id.upper(),
        "issue_summary": body.issue_summary,
        "priority": body.priority.upper(),
        "safety_decision": body.safety_decision.upper(),
        "status": "OPEN_DISPATCH_REQUIRED",
        "assigned_team": body.assigned_team,
        "created_at": _utc_now(),
    }

    TICKETS_DATABASE[ticket_id] = ticket_record
    return ticket_record
