"""
Utility functions for trough calculations.
"""
import re
import math

def parse_trough_label(label: str, default_deg: float = 20.0) -> float:
    """Parse a trough angle label to numeric degrees.

    Accepts formats like "20°", "20", or "0° (phẳng)".
    Returns default_deg when parsing fails.
    """
    try:
        if label is None or str(label).strip() == "":
            return float(default_deg)
        text = str(label).strip()
        # Flat belt special cases
        if "phẳng" in text.lower() or "0°" in text:
            return 0.0
        # Extract first number
        m = re.search(r"(\d+(?:\.\d+)?)", text)
        if m:
            return float(m.group(1))
        return float(default_deg)
    except Exception:
        return float(default_deg)

def capacity_from_geometry_tph(
    belt_width_mm: float,
    trough_angle_deg: float,
    surcharge_angle_deg: float,
    belt_speed_mps: float,
    material_density_tpm3: float,
) -> tuple:
    """
    Calculate theoretical belt capacity (TPH) and cross-section area (m2).

    Returns a tuple (Qt_calc_tph, cross_section_area_m2).
    """
    # Convert to meters for calculation
    belt_width_m = float(belt_width_mm) / 1000.0

    # Convert angles to radians
    trough_angle_rad = math.radians(float(trough_angle_deg))
    surcharge_angle_rad = math.radians(float(surcharge_angle_deg))

    # Cross-sectional area: bottom wedge + side rise with trough
    A_bottom = 0.25 * belt_width_m * belt_width_m * math.tan(surcharge_angle_rad)
    A_sides = (belt_width_m * belt_width_m / 8.0) * (1.0 - math.cos(trough_angle_rad))
    total_area_m2 = max(0.0, A_bottom + A_sides)

    # Volume flow (m3/s) = area * speed
    V = max(0.05, float(belt_speed_mps))
    volume_flow_m3ps = total_area_m2 * V

    # Density: input is tonnes/m3 → convert to kg/m3 for calculation then back to TPH
    rho_kgm3 = max(0.1, float(material_density_tpm3)) * 1000.0

    # TPH = m3/s * kg/m3 * 3600 / 1000
    qt_calc_tph = volume_flow_m3ps * rho_kgm3 * 3.6

    return qt_calc_tph, total_area_m2
