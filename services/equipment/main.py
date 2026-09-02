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
    # Household Appliances (Real Manufacturer Models)
    "HA-MICRO-01": {
        "equipment_id": "HA-MICRO-01",
        "name": "Panasonic Inverter Microwave/Convection Oven",
        "model": "Panasonic NN-C994S",
        "category": "Household Cooking",
        "location": "Kitchen Appliance Bay",
        "serial_number": "SN-PANA-NN-C994S",
        "specifications": {
            "microwave_power_w": 1000,
            "convection_power_w": 1400,
            "frequency_mhz": 2450,
            "high_voltage_capacitor": "0.95uF 2100V with 10M bleeder",
            "turntable_diameter_mm": 340,
            "safety_interlock": "Dual primary/secondary door microswitches",
        },
        "status": "OPERATIONAL",
        "installation_date": "2024-01-15",
    },
    "HA-TOAST-02": {
        "equipment_id": "HA-TOAST-02",
        "name": "Hamilton Beach 4-Slice Smart Toaster",
        "model": "Hamilton Beach 24121",
        "category": "Household Cooking",
        "location": "Kitchen Countertop",
        "serial_number": "SN-HB-24121",
        "specifications": {
            "rated_power_w": 1400,
            "voltage_v": 120,
            "slots": 4,
            "heating_element": "Nichrome wire wrapped mica boards",
            "latch_mechanism": "Magnetic hold-down carriage solenoid",
            "features": "Slide-out crumb tray, automatic shutoff anti-jam",
        },
        "status": "OPERATIONAL",
        "installation_date": "2024-03-10",
    },
    "HA-AIRFRY-03": {
        "equipment_id": "HA-AIRFRY-03",
        "name": "PowerXL Vortex Rapid-Air Digital Air Fryer",
        "model": "PowerXL HF-5096TS",
        "category": "Household Cooking",
        "location": "Kitchen Countertop",
        "serial_number": "SN-PXL-VAF-5QT",
        "specifications": {
            "rated_power_w": 1500,
            "voltage_v": 120,
            "capacity_qt": 5.0,
            "temp_range_f": "180F - 400F",
            "sensor": "NTC Temperature Thermistor 100k Ohm",
            "safety_cutoff": "Thermal fuse 216C / microswitch basket interlock",
        },
        "status": "OPERATIONAL",
        "installation_date": "2024-05-20",
    },
    "HA-WASH-04": {
        "equipment_id": "HA-WASH-04",
        "name": "Electrolux UltimateCare Front-Load Washing Machine",
        "model": "Electrolux EWF9042R7WB",
        "category": "Household Laundry",
        "location": "Utility / Laundry Room",
        "serial_number": "SN-ELUX-EWF9042",
        "specifications": {
            "capacity_kg": 9.0,
            "max_spin_speed_rpm": 1400,
            "motor_type": "EcoInverter Permanent Magnet Motor",
            "drain_pump": "Magnetic centrifugal pump 35W / 220V",
            "door_lock": "Electronic safety interlock with emergency pull cord",
            "diagnostics": "Error codes E10 (water fill), E20 (drain failure), E40 (door open), EH0 (voltage anomaly)",
        },
        "status": "OPERATIONAL",
        "installation_date": "2023-10-02",
    },
    "HA-OVEN-05": {
        "equipment_id": "HA-OVEN-05",
        "name": "Smeg 60cm Classic Pyrolytic Convection Oven",
        "model": "Smeg SFPA6300X",
        "category": "Household Cooking",
        "location": "Kitchen Cabinet Wall Unit",
        "serial_number": "SN-SMEG-SFPA6300X",
        "specifications": {
            "total_power_w": 3000,
            "voltage_v": 230,
            "cavity_volume_l": 70,
            "cleaning_mode": "Pyrolytic 500C with automatic electronic door lock",
            "heating_elements": "Top grill 1800W, Bottom bake 1200W, Circular fan 2000W",
            "cooling_system": "Tangential dual-speed cooling fan",
        },
        "status": "OPERATIONAL",
        "installation_date": "2023-08-14",
    },
    "HA-CHIM-06": {
        "equipment_id": "HA-CHIM-06",
        "name": "Broan 4-Way Convertible Range Hood / Chimney",
        "model": "Broan QL1 Series",
        "category": "Kitchen Ventilation",
        "location": "Cooktop Ventilation Wall Mount",
        "serial_number": "SN-BROAN-QL1-30",
        "specifications": {
            "airflow_cfm": 190,
            "speed_levels": 2,
            "filter_type": "Dual aluminum mesh grease filters with latch",
            "sound_level_sones": 6.0,
            "motor_specs": "120V / 1.9A shaded-pole motor with run capacitor",
            "damper": "Built-in 7-inch round & 3-1/4 x 10 inch backdraft damper",
        },
        "status": "OPERATIONAL",
        "installation_date": "2023-12-01",
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
