# -*- coding: utf-8 -*-
import math
from .specs import STANDARD_WIDTHS, ACTIVE_MATERIAL_DB

def optimize_belt_width(capacity_tph: float, density_tpm3: float, speed_mps: float) -> int:
    mass_flow = capacity_tph*1000/3600
    volume_flow = mass_flow/(density_tpm3*1000)
    required_area = volume_flow/max(speed_mps, 0.1)
    required_area *= 1.2
    est_width = math.sqrt(required_area/0.1)*1000
    return min(STANDARD_WIDTHS, key=lambda w: abs(w-est_width))

def optimize_speed(material_name: str, particle_mm: float, belt_width_mm: int) -> float:
    data = ACTIVE_MATERIAL_DB.get(material_name, {"v_max": 4.0})
    vmax = data.get("v_max", 4.0)
    if particle_mm > 200:
        rec = vmax*0.6
    elif particle_mm > 50:
        rec = vmax*0.8
    else:
        rec = vmax*0.9
    if belt_width_mm >= 1200:
        rec = min(rec*1.1, vmax)
    return round(rec, 2)
