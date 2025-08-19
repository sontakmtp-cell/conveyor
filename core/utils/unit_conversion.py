"""
Utility functions for unit conversions and mathematical operations.
"""
import math

def deg2rad(deg: float) -> float:
    """Convert degrees to radians."""
    return math.radians(deg)

def rad2deg(rad: float) -> float:
    """Convert radians to degrees."""
    return math.degrees(rad)

def mps_to_fpm(mps: float) -> float:
    """Convert meters per second to feet per minute."""
    return mps * 196.85  # 1 m/s = 196.85 ft/min

def kw_to_hp(kw: float) -> float:
    """Convert kilowatts to horsepower."""
    return kw * 1.34102  # 1 kW = 1.34102 hp

def mm_to_inch(mm: float) -> float:
    """Convert millimeters to inches."""
    return mm / 25.4  # 1 inch = 25.4 mm

def kg_to_lb(kg: float) -> float:
    """Convert kilograms to pounds."""
    return kg * 2.20462  # 1 kg = 2.20462 lbs

def m_to_ft(m: float) -> float:
    """Convert meters to feet."""
    return m * 3.28084  # 1 m = 3.28084 ft

def tph_to_tpd(tph: float) -> float:
    """Convert tonnes per hour to tonnes per day."""
    return tph * 24  # Assuming 24 hour operation
