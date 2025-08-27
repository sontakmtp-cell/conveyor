# -*- coding: utf-8 -*-
"""
Module chứa bảng tra Safety Factor thiết kế cho băng tải
Dựa trên tiêu chuẩn và hướng dẫn tính toán băng tải
"""

from typing import Optional, Union

# =========================
# SAFETY FACTOR LOOKUP TABLES (from PDF)
# =========================
# Keys:
#   group: "A" (mềm/hiền) hoặc "B" (cứng/cạnh sắc)
#   lump: "<30" hoặc ">=30"
#   duty bucket (phút):
#       Steel cord: "<3", "3-10", ">10"
#       Fabric: "<1", "1-3", "3-10", ">10"

STEEL_CORD_SF = {
    ("A", "<30", "<3"):   8.0,
    ("A", ">=30", "<3"):  8.0,
    ("B", "<30", "<3"):   8.0,
    ("B", ">=30", "<3"):  9.0,

    ("A", "<30", "3-10"): 7.0,
    ("A", ">=30", "3-10"):7.0,
    ("B", "<30", "3-10"): 7.0,
    ("B", ">=30", "3-10"):7.0,

    ("A", "<30", ">10"):  6.7,
    ("A", ">=30", ">10"): 6.7,
    ("B", "<30", ">10"):  6.7,
    ("B", ">=30", ">10"): 6.7,
}

FABRIC_SFZ = {
    ("A", "<30", "<1"):    11.0,
    ("A", ">=30", "<1"):   11.0,
    ("B", "<30", "<1"):    11.0,
    ("B", ">=30", "<1"):   12.0,

    ("A", "<30", "1-3"):   10.0,
    ("A", ">=30", "1-3"):  11.0,
    ("B", "<30", "1-3"):   11.0,
    ("B", ">=30", "1-3"):  11.0,

    ("A", "<30", "3-10"):  9.0,
    ("A", ">=30", "3-10"): 9.0,
    ("B", "<30", "3-10"):  10.0,
    ("B", ">=30", "3-10"): 10.0,

    ("A", "<30", ">10"):   8.0,
    ("A", ">=30", ">10"):  8.0,
    ("B", "<30", ">10"):   8.0,
    ("B", ">=30", ">10"):  8.0,
}

def _bucketize_duty_minutes(belt_type: str, duty_minutes: Optional[float]) -> str:
    """
    Trả về bucket chu kỳ theo bảng (đơn vị phút).
    
    Args:
        belt_type: Loại đai ("steel", "steel_cord", "st", "dây thép" hoặc fabric)
        duty_minutes: Chu kỳ làm việc tính bằng phút
    
    Returns:
        Bucket chu kỳ: "<3", "3-10", ">10" cho steel cord; "<1", "1-3", "3-10", ">10" cho fabric
    """
    m = float(duty_minutes or 0)
    
    if (belt_type or "").lower() in {"steel", "steel_cord", "st", "dây thép", "steel cord"}:
        if m < 3.0:
            return "<3"
        elif m <= 10.0:
            return "3-10"
        else:
            return ">10"
    else:
        if m < 1.0:
            return "<1"
        elif m <= 3.0:
            return "1-3"
        elif m <= 10.0:
            return "3-10"
        else:
            return ">10"

def _normalize_lump(lump_ge_30mm: Optional[bool]) -> str:
    """
    Chuẩn hóa cỡ hạt thành string.
    
    Args:
        lump_ge_30mm: True nếu cỡ hạt ≥ 30 mm, False nếu < 30 mm
    
    Returns:
        String: ">=30" hoặc "<30"
    """
    return ">=30" if bool(lump_ge_30mm) else "<30"

def lookup_sf_design(
    belt_type: str,
    group: str,                # "A" hoặc "B"
    lump_ge_30mm: bool,        # True nếu cỡ hạt ≥ 30 mm
    duty_minutes: Optional[float] # chu kỳ (phút)
) -> float:
    """
    Tra hệ số an toàn THIẾT KẾ (SF hoặc SFz) đúng bảng PDF.
    
    Args:
        belt_type: Loại đai ("steel", "steel_cord", "st", "dây thép" hoặc fabric)
        group: Nhóm vật liệu "A" (mềm/hiền) hoặc "B" (cứng/cạnh sắc)
        lump_ge_30mm: True nếu cỡ hạt ≥ 30 mm
        duty_minutes: Chu kỳ làm việc tính bằng phút
    
    Returns:
        Hệ số an toàn thiết kế (float)
    
    Raises:
        KeyError: Nếu không tìm thấy giá trị trong bảng tra
    """
    g = "A" if str(group).strip().upper() == "A" else "B"
    lump = _normalize_lump(lump_ge_30mm)
    bucket = _bucketize_duty_minutes(belt_type, duty_minutes)

    if (belt_type or "").lower() in {"steel", "steel_cord", "st", "dây thép", "steel cord"}:
        key = (g, lump, bucket)
        if key not in STEEL_CORD_SF:
            raise KeyError(f"Không tìm thấy SF cho steel cord với key: {key}")
        return STEEL_CORD_SF[key]
    else:
        # Fabric belts (EP, NN, PVC, Rubber)
        key = (g, lump, bucket)
        if key not in FABRIC_SFZ:
            raise KeyError(f"Không tìm thấy SFz cho fabric với key: {key}")
        return FABRIC_SFZ[key]

def get_sf_warning_thresholds(belt_type: str) -> tuple[float, float]:
    """
    Trả về ngưỡng cảnh báo cho SF thực.
    
    Args:
        belt_type: Loại đai
    
    Returns:
        Tuple (warning_yellow, warning_red): Ngưỡng cảnh báo vàng và đỏ
    """
    if (belt_type or "").lower() in {"steel", "steel_cord", "st", "dây thép", "steel cord"}:
        # Đai sợi thép: SF thực < 6 thì cảnh báo đỏ
        return 7.5, 6.0
    else:
        # Đai vải: SF thực < 8 thì cảnh báo đỏ
        return 10.0, 8.0

def validate_sf_design_inputs(
    belt_type: str,
    group: str,
    lump_ge_30mm: bool,
    duty_minutes: Optional[float]
) -> list[str]:
    """
    Kiểm tra tính hợp lệ của các tham số đầu vào.
    
    Args:
        belt_type: Loại đai
        group: Nhóm vật liệu
        lump_ge_30mm: Cỡ hạt
        duty_minutes: Chu kỳ làm việc
    
    Returns:
        Danh sách các lỗi (rỗng nếu hợp lệ)
    """
    errors = []
    
    if not belt_type:
        errors.append("Loại đai không được để trống")
    
    if group not in ["A", "B"]:
        errors.append("Nhóm vật liệu phải là 'A' hoặc 'B'")
    
    if duty_minutes is not None and duty_minutes < 0:
        errors.append("Chu kỳ làm việc không được âm")
    
    return errors
