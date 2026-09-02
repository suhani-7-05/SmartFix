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

    # Rule 4: Microwave High-Voltage Capacitor & Radiation Hazard (Household Appliance)
    if "microwave" in q_lower or eq_id == "HA-MICRO-01":
        # Check for lethal capacitor or opening casing while energized
        if "capacitor" in q_lower or "casing" in q_lower or "cabinet" in q_lower or "plugged in" in q_lower or "live" in q_lower:
            decision = "BLOCKED"
            rules_triggered.append("RULE-MW-01: Lethal High-Voltage Capacitor Hazard (>2,000V DC)")
            warnings.append("BLOCKED: Microwave high-voltage capacitor retains lethal 2,000V–4,000V DC charge even when unplugged. Direct contact can be fatal.")
            required_precautions.extend([
                "Unplug unit from AC power socket immediately.",
                "Discharge high-voltage capacitor using a 20k-Ohm 20W insulated HV discharge resistor probe before touching any internal part.",
                "Never test microwave with cabinet removed while connected to AC power.",
            ])
        elif "door open" in q_lower or "interlock" in q_lower or "bypass" in q_lower:
            decision = "BLOCKED"
            rules_triggered.append("RULE-MW-02: Microwave Radiation Exposure Hazard (2450 MHz)")
            warnings.append("BLOCKED: Operating microwave with door open or defeated interlock switches causes severe microwave radiation exposure.")
            required_precautions.extend([
                "Never defeat, bypass, or tamper with door safety interlock switches.",
                "Inspect door seal and choke cavity for physical damage or gaps.",
                "Perform RF leakage survey before returning unit to service (limit < 5mW/cm²).",
            ])
        elif decision != "BLOCKED":
            decision = "WARNING"
            rules_triggered.append("RULE-MW-03: General Microwave Electrical Safety")
            warnings.append("WARNING: Ensure unit is disconnected from mains before cleaning waveguide or turntable drive.")
            required_precautions.extend([
                "Unplug microwave from AC socket.",
                "Clean mica waveguide cover with damp cloth; do not operate if mica sheet is carbonized or burnt.",
            ])

    # Rule 5: Washing Machine Drum & Water Flood Hazard (Household Appliance)
    if "washing machine" in q_lower or "washer" in q_lower or eq_id == "HA-WASH-04":
        if "bypass door" in q_lower or "spin" in q_lower and ("open" in q_lower or "hand" in q_lower):
            decision = "BLOCKED"
            rules_triggered.append("RULE-WM-01: High-Speed Spinning Drum Entanglement Hazard")
            warnings.append("BLOCKED: Attempting to bypass door lock during spin cycle (1200 RPM) creates severe limb entanglement hazard.")
            required_precautions.extend([
                "Wait for drum to come to a complete standstill (minimum 2 minutes after power off).",
                "Use the manual emergency drain/door release cord located behind the drain pump filter access door.",
                "Never force open the electronic PTC thermal latch.",
            ])
        elif decision != "BLOCKED":
            decision = "WARNING"
            rules_triggered.append("RULE-WM-02: Water Valve Pressure & Shock Hazard")
            warnings.append("WARNING: Disconnect water supply taps and unplug unit before servicing drain pump filter or inlet solenoids.")
            required_precautions.extend([
                "Turn off cold and hot water inlet supply taps.",
                "Place a shallow tray under drain pump filter before unscrewing cap to catch residual water.",
                "Disconnect 230V mains plug.",
            ])

    # Rule 6: Toaster / Air Fryer / Convection Oven Thermal Hazards (Household Appliances)
    if any(app_word in q_lower for app_word in ["toaster", "air fryer", "airfryer", "oven"]) or eq_id in ["HA-TOAST-02", "HA-AIRFRY-03", "HA-OVEN-05"]:
        if decision != "BLOCKED":
            decision = "WARNING"
            rules_triggered.append("RULE-TH-01: High Temperature Burn & Heating Element Shock Hazard")
            warnings.append("WARNING: Internal heating elements operate above 200°C (400°F). Severe burn and electrical shock hazard.")
            required_precautions.extend([
                "Unplug appliance from wall socket.",
                "Allow appliance to cool down completely (minimum 30–45 minutes) before inspection or disassembly.",
                "Never insert metal utensils (forks/knives) into toaster slots while connected to power.",
                "Clean crumb trays and grease baskets regularly to prevent grease ignition fires.",
            ])

    # Rule 7: Range Hood / Kitchen Chimney Grease Hazard
    if "chimney" in q_lower or "range hood" in q_lower or "hood" in q_lower or eq_id == "HA-CHIM-06":
        if decision != "BLOCKED":
            decision = "WARNING"
            rules_triggered.append("RULE-CHIM-01: Range Hood Grease Fire & Blower Motor Hazard")
            warnings.append("WARNING: Accumulation of cooking grease in baffle filters creates a fire ignition hazard.")
            required_precautions.extend([
                "Switch off circuit breaker or unplug hood before removing filters.",
                "Soak aluminum or stainless steel baffle filters in warm degreaser solution monthly.",
                "Ensure blower motor is fully stopped before inspecting internal squirrel-cage impeller.",
            ])

    # Default ALLOWED precautions
    if not required_precautions:
        required_precautions.append("Follow manufacturer operating instructions and ensure appliance is unplugged before cleaning.")

    return {
        "equipment_id": eq_id,
        "decision": decision,
        "warnings": warnings,
        "rules_triggered": rules_triggered,
        "required_precautions": required_precautions,
        "evaluated_by": "SmartFix Safety Engine (Deterministic Rules)",
    }
