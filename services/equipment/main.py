"""
SmartFix Equipment Service — Exercise 4

Provides structured equipment information by Equipment ID.
"""

from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SmartFix Equipment Service", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured project equipment database
EQUIPMENT_DATABASE: dict[str, dict[str, Any]] = {
    "EQ-1023": {
        "equipment_id": "EQ-1023",
        "name": "High-Pressure Hydraulic Pump Assembly",
        "model": "HP-5000",
        "category": "Hydraulics",
        "location": "Substation B - Line 4",
        "serial_number": "SN-HP5000-8841",
        "specifications": {
            "operating_pressure_bar": 210,
            "max_pressure_bar": 250,
            "fluid_type": "ISO VG 46 Anti-Wear Hydraulic Oil",
            "rated_flow_lpm": 120,
            "max_temperature_c": 75,
        },
        "status": "OPERATIONAL",
        "installation_date": "2023-04-12",
    },
    "EQ-2045": {
        "equipment_id": "EQ-2045",
        "name": "Automated Package Transport Conveyor",
        "model": "CB-200",
        "category": "Material Transport",
        "location": "Warehouse Logistics Bay 2",
        "serial_number": "SN-CB200-5512",
        "specifications": {
            "max_speed_ms": 2.5,
            "belt_width_mm": 800,
            "belt_length_m": 50,
            "motor_power_kw": 15,
            "target_tension_kn": 45,
        },
        "status": "OPERATIONAL",
        "installation_date": "2022-09-18",
    },
    "EQ-3081": {
        "equipment_id": "EQ-3081",
        "name": "75kW 3-Phase AC Induction Motor Drive",
        "model": "IM-750",
        "category": "Electrical Drives",
        "location": "Compressor House Building 1",
        "serial_number": "SN-IM750-9920",
        "specifications": {
            "voltage_v": 400,
            "phase": 3,
            "rated_current_a": 135,
            "rated_power_kw": 75,
            "full_load_rpm": 1475,
            "max_stator_temp_c": 120,
        },
        "status": "MAINTENANCE_REQUIRED",
        "installation_date": "2021-11-05",
    },
}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "smartfix-equipment-service", "total_equipment": len(EQUIPMENT_DATABASE)}


@app.get("/equipment")
async def list_equipment():
    return list(EQUIPMENT_DATABASE.values())


@app.get("/equipment/{equipment_id}")
async def get_equipment(equipment_id: str):
    eq_id = equipment_id.upper()
    if eq_id not in EQUIPMENT_DATABASE:
        # Fallback for unrecognized IDs (fuzzy lookup or generic profile)
        return {
            "equipment_id": eq_id,
            "name": f"Generic DevOps Machine ({eq_id})",
            "model": "GENERIC-DEV-01",
            "category": "General Machinery",
            "location": "Main Assembly Line",
            "specifications": {"operating_voltage": "400V", "standard_load": "100%"},
            "status": "UNKNOWN",
        }
    return EQUIPMENT_DATABASE[eq_id]
