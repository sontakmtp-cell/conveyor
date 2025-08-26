# core/validators.py
# -*- coding: utf-8 -*-
from typing import List
from .models import ConveyorParameters
from .specs import ACTIVE_MATERIAL_DB
from .utils.trough_utils import parse_trough_label, capacity_from_geometry_tph

def validate_input_ranges(p: ConveyorParameters) -> List[str]:
    warns = []
    data = ACTIVE_MATERIAL_DB.get(p.material, {})
    max_speed = data.get("v_max", 4.0)

    # Kiểm tra V_mps chỉ khi nó không phải None
    if p.V_mps is not None and p.V_mps > max_speed:
        warns.append(f"Tốc độ băng {p.V_mps:.2f} m/s vượt khuyến cáo cho {p.material} ({max_speed:.2f} m/s).")
    if p.particle_size_mm > 100 and p.V_mps is not None and p.V_mps > 2.5:
        warns.append("Kích thước hạt lớn, nên giảm tốc độ băng (< 2.5 m/s) để hạn chế mài mòn và văng rơi.")
    if abs(p.inclination_deg) > 18:
        warns.append("Góc nghiêng lớn (>18°), cần kiểm tra trượt vật liệu hoặc dùng băng có gân.")
    if p.Qt_tph <= 0:
        warns.append("Lưu lượng phải lớn hơn 0.")
    if p.L_m <= 0:
        warns.append("Chiều dài băng phải lớn hơn 0.")

    if p.carrying_idler_spacing_m < 0.5 or p.carrying_idler_spacing_m > 3.0:
        warns.append("Khoảng cách con lăn tải nằm ngoài dải khuyến cáo [0.5, 3.0] m.")
    if p.return_idler_spacing_m < 1.0 or p.return_idler_spacing_m > 6.0:
        warns.append("Khoảng cách con lăn về nằm ngoài dải khuyến cáo [1.0, 6.0] m.")

    if p.ambient_temp_c > 40:
        warns.append("Nhiệt độ môi trường cao (>40°C). Cần kiểm tra derating motor và vật liệu bọc băng.")
    if p.altitude_m > 1000:
        warns.append("Độ cao >1000 m. Có thể cần derating công suất động cơ theo nhà sản xuất.")

    if p.explosion_proof:
        warns.append("Yêu cầu chống nổ: chọn motor/hộp số, cảm biến, tủ điện đạt chuẩn Ex.")
    if p.dusty_environment:
        warns.append("Môi trường bụi: ưu tiên idler kín bụi, che chắn hợp lý, tăng lịch bảo trì.")

    # Cross-section capacity check (sử dụng Qt nhập để sàng lọc sớm)
    try:
        trough_deg = parse_trough_label(getattr(p, "trough_angle_label", "20°"))
        surcharge_deg = float(getattr(p, "surcharge_angle_deg", 20.0) or 20.0)
        # Chỉ kiểm tra capacity khi V_mps không phải None
        if p.V_mps is not None:
            Qt_calc, _ = capacity_from_geometry_tph(p.B_mm, trough_deg, surcharge_deg, p.V_mps, p.density_tpm3)
            if p.Qt_tph > 1.05 * Qt_calc:
                warns.append(
                    f"Lưu lượng yêu cầu {p.Qt_tph:.1f} t/h vượt năng lực tiết diện Q_max≈{Qt_calc:.1f} t/h "
                    f"(B={p.B_mm} mm, máng≈{trough_deg:.0f}°, surcharge≈{surcharge_deg:.0f}°)."
                )
            elif p.Qt_tph > 0.95 * Qt_calc:
                warns.append(f"Lưu lượng yêu cầu đang tiệm cận năng lực tiết diện ({p.Qt_tph/Qt_calc*100:.1f}%).")
    except Exception:
        pass

    if not (0.7 <= p.motor_efficiency <= 0.99):
        warns.append("Hiệu suất động cơ nhập không hợp lý. Nên trong khoảng 0.85–0.97.")
    if not (0.7 <= p.gearbox_efficiency <= 0.99):
        warns.append("Hiệu suất hộp số nhập không hợp lý. Nên trong khoảng 0.9–0.98.")
    return warns

def validate_material_compatibility(p: ConveyorParameters) -> List[str]:
    warns = []
    data = ACTIVE_MATERIAL_DB.get(p.material, {})
    temp_max = data.get("temperature_max", 80)
    if p.material_temp_c > temp_max:
        warns.append(f"Nhiệt độ vật liệu {p.material_temp_c}°C vượt giới hạn cho vật liệu {p.material} ({temp_max}°C).")
    if data.get("corrosive", False) or p.corrosive_environment:
        if "PVC" not in p.belt_type and "Cao su" not in p.belt_type:
            warns.append("Vật liệu/MT ăn mòn, ưu tiên băng PVC hoặc cao su chịu ăn mòn.")
    return warns
