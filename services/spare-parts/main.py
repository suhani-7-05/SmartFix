"""
SmartFix Spare Parts Service — Exercise 4

Handles spare part inventory lookup and compatibility by Equipment ID.
"""

from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SmartFix Spare Parts Service", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SPARE_PARTS_DATABASE: dict[str, list[dict[str, Any]]] = {
    "EQ-1023": [
        {
            "part_number": "HP-FLTR-05",
            "name": "10-Micron Hydraulic Inlet Suction Filter Element",
            "compatibility": "Compatible with HP-5000 Series Pumps",
            "stock_status": "IN_STOCK",
            "quantity_available": 14,
            "unit_price_usd": 45.00,
            "location_bin": "Bin B-12",
        },
        {
            "part_number": "HP-SEAL-01",
            "name": "Viton High-Pressure Shaft Seal Ring",
            "compatibility": "Compatible with HP-5000 Series Pumps",
            "stock_status": "IN_STOCK",
            "quantity_available": 8,
            "unit_price_usd": 28.50,
            "location_bin": "Bin B-14",
        },
        {
            "part_number": "HP-VALV-210",
            "name": "210-Bar Primary Pressure Relief Valve",
            "compatibility": "Compatible with HP-5000 Series Pumps",
            "stock_status": "LOW_STOCK",
            "quantity_available": 2,
            "unit_price_usd": 180.00,
            "location_bin": "Bin C-04",
        },
    ],
    "EQ-2045": [
        {
            "part_number": "CB-BELT-200",
            "name": "Heavy-Duty Rubber Conveyor Belt (800mm x 50m)",
            "compatibility": "Compatible with CB-200 Conveyor",
            "stock_status": "IN_STOCK",
            "quantity_available": 3,
            "unit_price_usd": 650.00,
            "location_bin": "Rack R-01",
        },
        {
            "part_number": "CB-BEAR-6210",
            "name": "Double-Sealed Ball Bearing 6210-2RS",
            "compatibility": "Compatible with CB-200 Drive & Tail Pulley",
            "stock_status": "IN_STOCK",
            "quantity_available": 20,
            "unit_price_usd": 19.50,
            "location_bin": "Bin A-08",
        },
        {
            "part_number": "CB-BOLT-M20",
            "name": "Heavy Duty Pulley Tension Bolt Assembly M20",
            "compatibility": "Compatible with CB-200 Tail Pulley",
            "stock_status": "IN_STOCK",
            "quantity_available": 35,
            "unit_price_usd": 8.75,
            "location_bin": "Bin A-10",
        },
    ],
    "EQ-3081": [
        {
            "part_number": "IM-FAN-750",
            "name": "Polypropylene External Cooling Fan Shroud Assembly",
            "compatibility": "Compatible with IM-750 75kW Motor",
            "stock_status": "OUT_OF_STOCK",
            "quantity_available": 0,
            "unit_price_usd": 115.00,
            "location_bin": "Bin D-02",
        },
        {
            "part_number": "IM-BRG-6314",
            "name": "Drive-End Deep Groove Ball Bearing 6314-C3",
            "compatibility": "Compatible with IM-750 Motor DE Shaft",
            "stock_status": "IN_STOCK",
            "quantity_available": 4,
            "unit_price_usd": 72.00,
            "location_bin": "Bin D-05",
        },
        {
            "part_number": "IM-BRG-6312",
            "name": "Non-Drive-End Ball Bearing 6312-C3",
            "compatibility": "Compatible with IM-750 Motor NDE Shaft",
            "stock_status": "IN_STOCK",
            "quantity_available": 5,
            "unit_price_usd": 58.00,
            "location_bin": "Bin D-06",
        },
    ],
}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "smartfix-spare-parts-service", "total_parts": sum(len(v) for v in SPARE_PARTS_DATABASE.values())}


@app.get("/spare-parts/{equipment_id}")
async def get_spare_parts(equipment_id: str):
    eq_id = equipment_id.upper()
    parts = SPARE_PARTS_DATABASE.get(eq_id, [])
    return {
        "equipment_id": eq_id,
        "parts_count": len(parts),
        "parts": parts,
    }
