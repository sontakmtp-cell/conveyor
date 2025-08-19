# core/utils.py
# -*- coding: utf-8 -*-
import math
from typing import Tuple, Dict

def deg2rad(d: float) -> float:
    result = float(d) * math.pi / 180.0
    
    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG DEG2RAD: {d}° = {result} rad")
    
    return result

def parse_trough_label(label: str, default_deg: float = 20.0) -> float:
    print(f"DEBUG PARSE: START - label='{label}', default_deg={default_deg}")
    print(f"DEBUG PARSE: label type={type(label)}, label repr={repr(label)}")
    print(f"DEBUG PARSE: label length={len(str(label))}")
    
    if not label:
        print(f"DEBUG PARSE: label is empty, using default={default_deg}")
        return default_deg
    
    try:
        # Xử lý trường hợp đặc biệt "0° (phẳng)"
        print(f"DEBUG PARSE: checking for 'phẳng' in label...")
        if "phẳng" in str(label):
            print(f"DEBUG PARSE: label='{label}' contains 'phẳng', returning 0.0")
            return 0.0
        
        print(f"DEBUG PARSE: checking for '0°' in label...")
        if "0°" in str(label):
            print(f"DEBUG PARSE: label='{label}' contains '0°', returning 0.0")
            return 0.0
        
        print(f"DEBUG PARSE: no special cases found, trying regex...")
        import re
        m = re.search(r"(\d+(\.\d+)?)", str(label))
        if m:
            result = float(m.group(1))
            print(f"DEBUG PARSE: label='{label}' parsed to {result}")
            return result
        else:
            print(f"DEBUG PARSE: label='{label}' no match found, using default={default_deg}")
            return default_deg
    except Exception as e:
        print(f"DEBUG PARSE: label='{label}' error: {e}, using default={default_deg}")
        import traceback
        traceback.print_exc()
        return default_deg

# --- [BẮT ĐẦU NÂNG CẤP] ---
# Bảng 4: Hệ số K tính toán mặt cắt dòng chảy (số hóa từ PDF)
# Dùng cho băng tải máng 3 con lăn.
K_FACTOR_TABLE_3_ROLL: Dict[int, Dict[int, float]] = {
    # góc máng -> {góc mái -> K}
    10: {10: 0.0649, 20: 0.0945, 30: 0.1253},
    15: {10: 0.0817, 20: 0.1106, 30: 0.1408}, # Note: PDF có thể in nhầm thứ tự 10,20
    20: {10: 0.0963, 20: 0.1245, 30: 0.1538},
    25: {10: 0.1113, 20: 0.1381, 30: 0.1661}, # Note: PDF có thể in nhầm thứ tự 10,20
    30: {10: 0.1232, 20: 0.1488, 30: 0.1754},
    35: {10: 0.1348, 20: 0.1588, 30: 0.1837},
    40: {10: 0.1426, 20: 0.1649, 30: 0.1882},
    45: {10: 0.1500, 20: 0.1704, 30: 0.1916}, # Note: PDF có thể in nhầm thứ tự 10,20
}
# Băng phẳng
K_FACTOR_TABLE_FLAT: Dict[int, float] = {10: 0.0295, 20: 0.0591, 30: 0.0906}


def _interpolate_k(angle: float, k_map: Dict[int, float]) -> float:
    """Nội suy tuyến tính giá trị K từ một map."""
    keys = sorted(k_map.keys())
    if angle <= keys[0]:
        k_val = k_map[keys[0]]
        print(f"DEBUG INTERPOLATE: angle={angle} <= {keys[0]}, using K={k_val}")
        return k_val
    if angle >= keys[-1]:
        k_val = k_map[keys[-1]]
        print(f"DEBUG INTERPOLATE: angle={angle} >= {keys[-1]}, using K={k_val}")
        return k_val
    for i in range(len(keys) - 1):
        if keys[i] <= angle <= keys[i+1]:
            x0, y0 = keys[i], k_map[keys[i]]
            x1, y1 = keys[i+1], k_map[keys[i+1]]
            k_val = y0 + (y1 - y0) * (angle - x0) / (x1 - x0)
            print(f"DEBUG INTERPOLATE: interpolating between ({x0}, {y0}) and ({x1}, {y1}) for angle={angle}, K={k_val}")
            return k_val
    k_val = k_map[keys[len(keys) // 2]] # Fallback
    print(f"DEBUG INTERPOLATE: fallback to middle value, K={k_val}")
    return k_val

def get_k_factor(trough_deg: float, surcharge_deg: float) -> float:
    """
    Tra cứu hệ số K từ Bảng 4 trong PDF, có nội suy.
    """
    trough_deg = float(trough_deg)
    surcharge_deg = float(surcharge_deg)

    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG K_FACTOR: trough_deg={trough_deg}, surcharge_deg={surcharge_deg}")

    if trough_deg < 5: # Coi như băng phẳng
        k_flat = _interpolate_k(surcharge_deg, K_FACTOR_TABLE_FLAT)
        print(f"DEBUG K_FACTOR: Using flat belt table, K={k_flat}")
        return k_flat

    # Nội suy theo góc mái trước
    k_at_surcharge = {}
    trough_angles = sorted(K_FACTOR_TABLE_3_ROLL.keys())
    for t_ang in trough_angles:
        k_at_surcharge[t_ang] = _interpolate_k(surcharge_deg, K_FACTOR_TABLE_3_ROLL[t_ang])

    # Nội suy theo góc máng sau
    k_trough = _interpolate_k(trough_deg, k_at_surcharge)
    print(f"DEBUG K_FACTOR: Using trough table, K={k_trough}")
    return k_trough


def cross_section_area_m2(B_mm: int, trough_deg: float, surcharge_deg: float) -> float:
    """
    Tính diện tích mặt cắt ngang theo Công thức (3) và Bảng 4, trang 7, PDF.
    A = K * (0.9*B - 0.05)^2
    """
    B_m = max(0.3, float(B_mm) / 1000.0)
    K = get_k_factor(trough_deg, surcharge_deg)
    
    # Chiều rộng hiệu quả, không được nhỏ hơn 0
    effective_width_term = max(0, 0.9 * B_m - 0.05)
    
    # Xử lý đặc biệt cho băng tải phẳng: sử dụng chiều rộng thực tế thay vì hiệu quả
    if trough_deg < 5:  # Băng tải phẳng
        # Với băng tải phẳng, sử dụng chiều rộng thực tế để tránh diện tích quá nhỏ
        effective_width_term = max(0.1, B_m * 0.8)  # Sử dụng 80% chiều rộng thực tế
        print(f"DEBUG CROSS_SECTION: Flat belt detected, using effective_width_term={effective_width_term}")
    
    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG CROSS_SECTION: B_mm={B_mm}, trough_deg={trough_deg}, surcharge_deg={surcharge_deg}")
    print(f"DEBUG CROSS_SECTION: B_m={B_m}, K={K}, effective_width_term={effective_width_term}")
    print(f"DEBUG CROSS_SECTION: cross_section_area={K * (effective_width_term ** 2)}")
    
    return K * (effective_width_term ** 2)


def capacity_from_geometry_tph(B_mm: int, trough_deg: float, surcharge_deg: float,
                               V_mps: float, density_tpm3: float) -> Tuple[float, float]:
    """
    Tính lưu lượng dựa trên hình học theo Công thức (1), trang 6, PDF.
    Qt = 3600 * A * V * gamma (chuyển đổi từ công thức gốc)
    """
    A = cross_section_area_m2(B_mm, trough_deg, surcharge_deg)
    V = max(0.05, float(V_mps))
    rho = max(0.1, float(density_tpm3))
    
    # Công thức gốc: Qt (tấn/h) = 60 * A(m2) * V(m/phút) * rho(tấn/m3)
    # V(m/phút) = V(m/s) * 60
    # => Qt = 60 * A * (V_mps * 60) * rho = 3600 * A * V_mps * rho
    qt_calc = 3600 * A * V * rho
    
    # Xử lý trường hợp diện tích mặt cắt quá nhỏ (có thể do băng tải phẳng)
    if A < 1e-6:  # Diện tích gần như bằng 0
        print(f"DEBUG CAPACITY: Warning - Cross section area too small ({A}), using fallback calculation")
        # Sử dụng phương pháp dự phòng: ước tính dựa trên chiều rộng và tốc độ
        B_m = max(0.3, float(B_mm) / 1000.0)
        # Ước tính diện tích dự phòng: sử dụng 60% chiều rộng và chiều cao ước tính
        fallback_height = max(0.05, surcharge_deg / 100.0)  # Chiều cao ước tính từ góc surcharge
        A_fallback = B_m * fallback_height * 0.6  # Hệ số 0.6 để bù trừ
        qt_calc = 3600 * A_fallback * V * rho
        A = A_fallback
        print(f"DEBUG CAPACITY: Using fallback: A_fallback={A_fallback}, qt_calc={qt_calc}")
    
    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG CAPACITY: A={A}, V={V}, rho={rho}")
    print(f"DEBUG CAPACITY: qt_calc={qt_calc}")
    
    return qt_calc, A
# --- [KẾT THÚC NÂNG CẤP] ---