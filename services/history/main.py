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
    # Household Appliances Service Records
    "HA-MICRO-01": [
        {
            "event_id": "EVT-MICRO-01",
            "date": "2026-06-18",
            "type": "CORRECTIVE_MAINTENANCE",
            "symptom": "Turntable rotates, display counts down, interior light on, but food completely cold",
            "root_cause": "High-voltage rectifier diode breakdown (shorted) causing 0V DC at magnetron cathode",
            "action_taken": "Discharged HV capacitor. Replaced high-voltage diode (part #MW-DIO-2CL4512) and verified 0.2 mW/cm² RF leakage with Holaday meter.",
            "technician": "A. Chen (Consumer Electronics Specialist)",
            "resolution_status": "RESOLVED",
        },
    ],
    "HA-TOAST-02": [
        {
            "event_id": "EVT-TOAST-01",
            "date": "2026-04-12",
            "type": "CLEANING_REPAIR",
            "symptom": "Carriage lever pops up immediately when pressed down; will not stay latched",
            "root_cause": "Heavy accumulation of carbonized bread crumbs blocking solenoid electromagnet armature",
            "action_taken": "Removed slide-out crumb tray, vacuumed lower carriage cavity, and burnished solenoid contact points.",
            "technician": "K. Patel (Appliance Tech)",
            "resolution_status": "RESOLVED",
        },
    ],
    "HA-AIRFRY-03": [
        {
            "event_id": "EVT-AIRFRY-01",
            "date": "2026-05-30",
            "type": "SENSOR_REPAIR",
            "symptom": "Air fryer powers on and beeps 5 times, display flashes Error E1 and stops heating",
            "root_cause": "NTC temperature sensor thermistor probe open-circuit due to fatigue wire bending",
            "action_taken": "Replaced 100k Ohm NTC sensor harness (part #AF-NTC-100K) and calibrated temperature at 350°F.",
            "technician": "L. Gomez (Service Tech)",
            "resolution_status": "RESOLVED",
        },
    ],
    "HA-WASH-04": [
        {
            "event_id": "EVT-WASH-01",
            "date": "2026-07-14",
            "type": "DRAIN_CLEARANCE",
            "symptom": "Washing machine stops mid-cycle, beeps, and displays Error Err2 with tub full of water",
            "root_cause": "Metallic hairpin and coin lodged in drain pump impeller chamber restricting rotation",
            "action_taken": "Drained water via emergency drain tube. Unscrewed drain pump lint filter, cleared foreign objects, and verified drain test cycle.",
            "technician": "J. Wilson (Master Laundry Tech)",
            "resolution_status": "RESOLVED",
        },
    ],
    "HA-OVEN-05": [
        {
            "event_id": "EVT-OVEN-01",
            "date": "2026-02-28",
            "type": "SAFETY_INSPECTION",
            "symptom": "Oven door remained locked for 3 hours after pyrolytic cleaning cycle finished",
            "root_cause": "Tangential cooling fan air intake clogged with cabinet dust, delaying cavity cool-down below 280°C threshold",
            "action_taken": "Vacuumed upper cooling vents. Electronic door latch released normally once cavity reached 260°C.",
            "technician": "M. Weber (Kitchen Appliance Tech)",
            "resolution_status": "RESOLVED",
        },
    ],
    "HA-CHIM-06": [
        {
            "event_id": "EVT-CHIM-01",
            "date": "2026-08-05",
            "type": "PREVENTIVE_MAINTENANCE",
            "symptom": "Loud rattling vibration on high speed setting and reduced smoke extraction suction",
            "root_cause": "Baffle grease filters saturated; grease residue accumulated unevenly on centrifugal blower blades causing dynamic imbalance",
            "action_taken": "Degreased stainless steel baffle filters in ultrasonic bath and balanced squirrel-cage fan wheel.",
            "technician": "S. Rao (Ventilation Specialist)",
            "resolution_status": "RESOLVED",
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
