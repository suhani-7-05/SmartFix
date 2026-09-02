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
    # Household Appliance Spare Parts
    "HA-MICRO-01": [
        {
            "part_number": "MW-MAG-2M261",
            "name": "Panasonic 2M261-M32 Inverter Magnetron Tube",
            "compatibility": "Compatible with Panasonic NN-C994S & Inverter Series",
            "stock_status": "IN_STOCK",
            "quantity_available": 6,
            "unit_price_usd": 68.00,
            "location_bin": "Aisle E-01",
        },
        {
            "part_number": "MW-DIO-2CL4512",
            "name": "High-Voltage Rectifier Diode (12kV / 350mA)",
            "compatibility": "Compatible with Panasonic NN-C994S Microwave",
            "stock_status": "IN_STOCK",
            "quantity_available": 25,
            "unit_price_usd": 8.50,
            "location_bin": "Bin E-03",
        },
        {
            "part_number": "MW-MICA-PANA",
            "name": "Waveguide Mica Cover Sheet (110mm x 125mm)",
            "compatibility": "Compatible with Panasonic Microwave Cavities",
            "stock_status": "IN_STOCK",
            "quantity_available": 40,
            "unit_price_usd": 5.00,
            "location_bin": "Bin E-05",
        },
    ],
    "HA-TOAST-02": [
        {
            "part_number": "TOAST-SOL-120",
            "name": "Hold-Down Carriage Solenoid Magnet Assembly",
            "compatibility": "Compatible with Hamilton Beach 24121 4-Slice Toaster",
            "stock_status": "IN_STOCK",
            "quantity_available": 12,
            "unit_price_usd": 14.50,
            "location_bin": "Bin T-02",
        },
        {
            "part_number": "TOAST-ELEM-HB4",
            "name": "Replacement Nichrome Wire Mica Heating Panel Set",
            "compatibility": "Compatible with Hamilton Beach 4-Slice Slots",
            "stock_status": "IN_STOCK",
            "quantity_available": 10,
            "unit_price_usd": 18.00,
            "location_bin": "Bin T-04",
        },
    ],
    "HA-AIRFRY-03": [
        {
            "part_number": "AF-NTC-100K",
            "name": "High-Temp NTC Thermistor Temperature Sensor Probe (100k Ohm)",
            "compatibility": "Compatible with PowerXL Vortex 2qt-7qt Series",
            "stock_status": "IN_STOCK",
            "quantity_available": 18,
            "unit_price_usd": 12.00,
            "location_bin": "Bin AF-01",
        },
        {
            "part_number": "AF-FUSE-216",
            "name": "Thermal Cut-off Fuse (216°C / 10A / 250V)",
            "compatibility": "Universal Air Fryer & Convection Safety Cutoff",
            "stock_status": "IN_STOCK",
            "quantity_available": 50,
            "unit_price_usd": 4.25,
            "location_bin": "Bin AF-03",
        },
    ],
    "HA-WASH-04": [
        {
            "part_number": "WM-PUMP-HAIER",
            "name": "Magnetic Centrifugal Drain Pump Motor (30W / 220-240V)",
            "compatibility": "Compatible with Haier Drum Washer Series",
            "stock_status": "IN_STOCK",
            "quantity_available": 14,
            "unit_price_usd": 32.00,
            "location_bin": "Shelf W-10",
        },
        {
            "part_number": "WM-LOCK-DL01",
            "name": "PTC Electronic Door Interlock Switch Latch",
            "compatibility": "Compatible with Haier Automatic Drum Washers",
            "stock_status": "IN_STOCK",
            "quantity_available": 9,
            "unit_price_usd": 24.50,
            "location_bin": "Bin W-12",
        },
    ],
    "HA-OVEN-05": [
        {
            "part_number": "OV-ELEM-2000W",
            "name": "Circular Convection Fan Heating Element (2000W / 230V)",
            "compatibility": "Compatible with Smeg SFPA6300X & 60cm Ovens",
            "stock_status": "IN_STOCK",
            "quantity_available": 7,
            "unit_price_usd": 48.00,
            "location_bin": "Shelf OV-02",
        },
        {
            "part_number": "OV-THERM-300",
            "name": "Manual Reset Safety Limiter Thermostat (300°C)",
            "compatibility": "Compatible with Smeg Pyrolytic Ovens",
            "stock_status": "IN_STOCK",
            "quantity_available": 15,
            "unit_price_usd": 21.00,
            "location_bin": "Bin OV-05",
        },
    ],
    "HA-CHIM-06": [
        {
            "part_number": "CHIM-FLTR-ALUM",
            "name": "Aluminum Mesh Grease Filter with Quick-Release Latch (Pair)",
            "compatibility": "Compatible with Broan QL1 Series 30-inch Hoods",
            "stock_status": "IN_STOCK",
            "quantity_available": 30,
            "unit_price_usd": 26.00,
            "location_bin": "Rack CH-01",
        },
        {
            "part_number": "CHIM-WHEEL-CENT",
            "name": "Dynamically Balanced Centrifugal Blower Wheel Impeller",
            "compatibility": "Compatible with Broan QL1 Series Blowers",
            "stock_status": "IN_STOCK",
            "quantity_available": 8,
            "unit_price_usd": 34.00,
            "location_bin": "Rack CH-03",
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
