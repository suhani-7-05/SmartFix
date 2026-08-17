"""
SmartFix Safety Engine Service — Exercise 4

Evaluates explicit rule-based safety constraints.
Returns ALLOWED / WARNING / BLOCKED with required safety precautions.
"""

from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="SmartFix Safety Engine Service", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SafetyEvaluationRequest(BaseModel):
    equipment_id: str = Field(..., description="Target equipment ID (e.g., EQ-1023)")
    question: str = Field(..., description="User troubleshooting question text")
    equipment_data: dict[str, Any] = Field(default_factory=dict, description="Equipment metadata")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "smartfix-safety-engine", "rules_engine": "Deterministic-RuleSet-v1"}


@app.post("/safety/evaluate")
async def evaluate_safety(body: SafetyEvaluationRequest) -> dict[str, Any]:
    """
    Deterministic Safety Evaluation Engine.

    Rule Sets:
    1. BLOCKED: Operations involving high voltage terminal boxes (>400V) without LOTO,
       or inspecting moving conveyor belts without stopping drive motor.
    2. WARNING: Hydraulic pressure checks (>200 bar), thermal inspection (>75°C), or live current checks.
    3. ALLOWED: General inspection, manual readouts, or standard fluid level checks with PPE.
    """
    q_lower = body.question.lower()
    eq_id = body.equipment_id.upper()

    warnings = []
    rules_triggered = []
    required_precautions = []
    decision = "ALLOWED"

    # Rule 1: High Voltage 400V Terminal Box (BLOCKED if live terminal opening attempted without LOTO)
    if "400v" in q_lower or "terminal box" in q_lower or "high voltage" in q_lower or eq_id == "EQ-3081":
        if "open terminal" in q_lower or "touch leads" in q_lower or "live" in q_lower:
            decision = "BLOCKED"
            rules_triggered.append("RULE-HV-01: High Voltage Isolation Mandatory")
            warnings.append("BLOCKED: Attempting to access 400V live electrical terminal box poses fatal shock risk.")
            required_precautions.extend([
                "Perform main breaker Lockout/Tagout (LOTO).",
                "Verify Zero Energy State with calibrated multimeter before touching leads.",
                "Discharge power factor correction capacitors.",
            ])

    # Rule 2: Moving Conveyor Inspection (BLOCKED if inspecting belt while running)
    if "conveyor" in q_lower or "belt" in q_lower or eq_id == "EQ-2045":
        if "moving" in q_lower or "running" in q_lower or "while operating" in q_lower:
            decision = "BLOCKED"
            rules_triggered.append("RULE-CV-02: Moving Pinch-Point Hazard Prohibition")
            warnings.append("BLOCKED: Inspecting or placing hands near moving conveyor pulleys is strictly prohibited.")
            required_precautions.extend([
                "Press Emergency Stop (E-STOP) button.",
                "Apply padlocks to main isolator switch.",
                "Verify drive motor is fully stopped before clearing belt jams.",
            ])
        elif decision != "BLOCKED":
            decision = "WARNING"
            rules_triggered.append("RULE-CV-01: Conveyor Tension & E-Stop Precaution")
            warnings.append("WARNING: E-Stop pull-cord must be verified before working near tension pulleys.")
            required_precautions.extend([
                "Ensure E-Stop pull-cord switches are operational.",
                "Wear cut-resistant safety gloves.",
            ])

    # Rule 3: High Pressure Hydraulics (WARNING for pressure > 200 bar)
    if "pressure" in q_lower or "hydraulic" in q_lower or "fluid" in q_lower or eq_id == "EQ-1023":
        if decision != "BLOCKED":
            decision = "WARNING"
            rules_triggered.append("RULE-HYD-01: High Pressure Fluid Injection Hazard")
            warnings.append("WARNING: System operates at high hydraulic pressure (210 bar). High pressure oil injection can cause severe injury.")
            required_precautions.extend([
                "Perform LOTO on main drive motor.",
                "Verify pressure gauge reads 0 bar before loosening any hydraulic line or valve.",
                "Wear protective safety goggles and heat-resistant gloves.",
            ])

    # Default ALLOWED precautions
    if not required_precautions:
        required_precautions.append("Wear standard industrial PPE (safety glasses, steel-toed boots, protective gloves).")

    return {
        "equipment_id": eq_id,
        "decision": decision,
        "warnings": warnings,
        "rules_triggered": rules_triggered,
        "required_precautions": required_precautions,
        "evaluated_by": "SmartFix Safety Engine (Deterministic Rules)",
    }
