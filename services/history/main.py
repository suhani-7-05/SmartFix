"""
SmartFix History Service — Exercise 4

Stores previous maintenance, failure, and repair events by Equipment ID.
"""

from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SmartFix Maintenance History Service", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HISTORY_DATABASE: dict[str, list[dict[str, Any]]] = {
    "EQ-1023": [
        {
            "event_id": "EVT-1023-01",
            "date": "2026-05-10",
            "type": "CORRECTIVE_MAINTENANCE",
            "symptom": "Low hydraulic pressure (dropped to 130 bar)",
            "root_cause": "Inlet suction filter clogging (part #HP-FLTR-05) causing pump cavitation",
            "action_taken": "Replaced 10-micron inlet filter element and flushed hydraulic reservoir.",
            "technician": "T. Vance (Senior Maintenance Tech)",
            "resolution_status": "RESOLVED",
        },
        {
            "event_id": "EVT-1023-02",
            "date": "2025-11-22",
            "type": "PREVENTIVE_MAINTENANCE",
            "symptom": "Scheduled annual overhaul",
            "root_cause": "Normal operational wear on Viton shaft seals",
            "action_taken": "Replaced Viton shaft seal ring (part #HP-SEAL-01) and recalibrated primary relief valve to 210 bar.",
            "technician": "R. Sharma (Hydraulics Specialist)",
            "resolution_status": "RESOLVED",
        },
    ],
    "EQ-2045": [
        {
            "event_id": "EVT-2045-01",
            "date": "2026-03-14",
            "type": "EMERGENCY_REPAIR",
            "symptom": "Drive belt slippage and rubber smell during peak transport load",
            "root_cause": "Belt tension dropped below 30 kN specification due to tail pulley bolt loosening",
            "action_taken": "Re-tensioned tail pulley adjustment bolts (part #CB-BOLT-M20) to 45 kN and applied thread-locking compound.",
            "technician": "M. Jenkins (Mechanic)",
            "resolution_status": "RESOLVED",
        },
    ],
    "EQ-3081": [
        {
            "event_id": "EVT-3081-01",
            "date": "2026-07-02",
            "type": "INSPECTION_WARNING",
            "symptom": "Stator temperature trip at 122°C and high non-drive-end bearing vibration (5.1 mm/s RMS)",
            "root_cause": "Dust buildup on rear cooling fan shroud and bearing lubricant breakdown",
            "action_taken": "Cleaned fan fins and re-greased DE/NDE bearings. Recommended bearing replacement on next scheduled shutdown.",
            "technician": "D. Miller (Electrical Tech)",
            "resolution_status": "MONITORING_REQUIRED",
        },
    ],
}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "smartfix-history-service", "total_records": sum(len(v) for v in HISTORY_DATABASE.values())}


@app.get("/history/{equipment_id}")
async def get_equipment_history(equipment_id: str):
    eq_id = equipment_id.upper()
    records = HISTORY_DATABASE.get(eq_id, [])
    return {
        "equipment_id": eq_id,
        "event_count": len(records),
        "history": records,
    }
