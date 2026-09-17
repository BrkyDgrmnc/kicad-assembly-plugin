"""
KiCad 10 Assembly & Fabrication Tool - Configuration and Preset Definitions
"""

import os
import json

APP_NAME = "KiCad Assembly & Fabrication Tool"
APP_VERSION = "1.0.0"
AUTHOR = "Berkay Değirmenci"

# Default Custom Assembly Vendor Format
CUSTOM_USER_VENDOR_PRESET = {
    "id": "custom_user_vendor",
    "name": "Custom Assembly Vendor Format",
    "description": "RefDes, PatternName, Type, ValUe, Layer, LocationX, LocationY, Rotation, smd value",
    "file_extension": ".csv",
    "delimiter": ",",
    "decimal_separator": ".",
    "include_header": True,
    "columns": [
        {"header": "RefDes", "template": "{Reference}"},
        {"header": "PatternName", "template": "{Footprint}"},
        {"header": "Type", "template": "{Footprint}"},
        {"header": "ValUe", "template": "{Value}"},
        {"header": "Layer", "template": "{Layer}"},
        {"header": "LocationX", "template": "{X}"},
        {"header": "LocationY", "template": "{Y}"},
        {"header": "Rotation", "template": "{Rotation}"},
        {"header": "smd value", "template": "{Footprint}-{Value}"}
    ]
}

# JLCPCB CPL Preset
JLCPCB_CPL_PRESET = {
    "id": "jlcpcb_cpl",
    "name": "JLCPCB - CPL (Pick & Place)",
    "description": "CPL CSV file for JLCPCB assembly service",
    "file_extension": ".csv",
    "delimiter": ",",
    "decimal_separator": ".",
    "include_header": True,
    "columns": [
        {"header": "Designator", "template": "{Reference}"},
        {"header": "Val", "template": "{Value}"},
        {"header": "Package", "template": "{Footprint}"},
        {"header": "Mid E", "template": "{X}"},
        {"header": "Mid Y", "template": "{Y}"},
        {"header": "Rotation", "template": "{Rotation}"},
        {"header": "Layer", "template": "{Layer}"}
    ]
}

# JLCPCB BOM Preset
JLCPCB_BOM_PRESET = {
    "id": "jlcpcb_bom",
    "name": "JLCPCB - BOM (Bill of Materials)",
    "description": "BOM CSV file for JLCPCB assembly service",
    "file_extension": ".csv",
    "delimiter": ",",
    "decimal_separator": ".",
    "include_header": True,
    "columns": [
        {"header": "Comment", "template": "{Value}"},
        {"header": "Designator", "template": "{Reference}"},
        {"header": "Footprint", "template": "{Footprint}"},
        {"header": "LCSC Part #", "template": "{LCSC}"}
    ]
}

# PCBWay CPL Preset
PCBWAY_CPL_PRESET = {
    "id": "pcbway_cpl",
    "name": "PCBWay - CPL (Pick & Place)",
    "description": "CPL CSV file for PCBWay assembly service",
    "file_extension": ".csv",
    "delimiter": ",",
    "decimal_separator": ".",
    "include_header": True,
    "columns": [
        {"header": "Designator", "template": "{Reference}"},
        {"header": "Center-X(mm)", "template": "{X}"},
        {"header": "Center-Y(mm)", "template": "{Y}"},
        {"header": "Layer", "template": "{Layer}"},
        {"header": "Rotation", "template": "{Rotation}"},
        {"header": "Comment", "template": "{Value}"}
    ]
}

# NeoDen PnP Machine Preset (NeoDen4 / YY1)
NEODEN_MACHINE_PRESET = {
    "id": "neoden_pnp",
    "name": "Pick & Place Machine - NeoDen (YY1 / NeoDen4)",
    "description": "CSV output for NeoDen PnP assembly machines",
    "file_extension": ".csv",
    "delimiter": ",",
    "decimal_separator": ".",
    "include_header": True,
    "columns": [
        {"header": "Designator", "template": "{Reference}"},
        {"header": "Footprint", "template": "{Footprint}"},
        {"header": "Mid X", "template": "{X}"},
        {"header": "Mid Y", "template": "{Y}"},
        {"header": "Rotation", "template": "{Rotation}"},
        {"header": "Layer", "template": "{Layer}"},
        {"header": "Comment", "template": "{Value}"}
    ]
}

# Charmhigh PnP Machine Preset
CHARMHIGH_MACHINE_PRESET = {
    "id": "charmhigh_pnp",
    "name": "Pick & Place Machine - Charmhigh (CHMT Series)",
    "description": "CSV output for Charmhigh PnP assembly machines",
    "file_extension": ".csv",
    "delimiter": ",",
    "decimal_separator": ".",
    "include_header": True,
    "columns": [
        {"header": "Components", "template": "{Reference}"},
        {"header": "Package", "template": "{Footprint}"},
        {"header": "X", "template": "{X}"},
        {"header": "Y", "template": "{Y}"},
        {"header": "Rotation", "template": "{Rotation}"},
        {"header": "Layer", "template": "{Layer}"},
        {"header": "Value", "template": "{Value}"}
    ]
}

# LitePlacer Machine Preset
LITEPLACER_MACHINE_PRESET = {
    "id": "liteplacer_pnp",
    "name": "Pick & Place Machine - LitePlacer",
    "description": "CSV output for LitePlacer PnP assembly machines",
    "file_extension": ".csv",
    "delimiter": ",",
    "decimal_separator": ".",
    "include_header": True,
    "columns": [
        {"header": "ID", "template": "{Reference}"},
        {"header": "X", "template": "{X}"},
        {"header": "Y", "template": "{Y}"},
        {"header": "Rotation", "template": "{Rotation}"},
        {"header": "Value", "template": "{Value}"},
        {"header": "Footprint", "template": "{Footprint}"},
        {"header": "PartNumber", "template": "{MPN}"},
        {"header": "Layer", "template": "{Layer}"}
    ]
}

ALL_PRESETS = [
    CUSTOM_USER_VENDOR_PRESET,
    JLCPCB_CPL_PRESET,
    JLCPCB_BOM_PRESET,
    PCBWAY_CPL_PRESET,
    NEODEN_MACHINE_PRESET,
    CHARMHIGH_MACHINE_PRESET,
    LITEPLACER_MACHINE_PRESET
]

# Standard Footprint Rotation Offset Rules (JLCPCB & PnP Standards)
DEFAULT_ROTATION_OFFSETS = {
    "SOT-23": 180.0,
    "SOT-23-3": 180.0,
    "SOT-23-5": 180.0,
    "SOT-23-6": 180.0,
    "SOT-89": 180.0,
    "SOT-223": 180.0,
    "SOP-8": -90.0,
    "SOIC-8": -90.0,
    "SOIC-16": -90.0,
    "SSOP-8": -90.0,
    "TSSOP-8": -90.0,
    "LQFP-48": -90.0,
    "QFN-16": -90.0,
    "QFN-32": -90.0,
    "QFN-48": -90.0,
    "D_SMA": 180.0,
    "D_SMB": 180.0,
    "D_SMC": 180.0,
    "D_SOD-123": 180.0,
    "D_SOD-323": 180.0,
    "CP_EIA-3216-18_KEMET-A": 180.0,
    "CP_EIA-3528-21_KEMET-B": 180.0,
    "CP_EIA-6032-28_KEMET-C": 180.0,
}
