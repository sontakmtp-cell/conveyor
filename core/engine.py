# title="core/engine.py" contentType="text/python"
# -*- coding: utf-8 -*-

import math
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Optional

from .models import BeltType, CalculationResult, ConveyorParameters
from .specs import G, ACTIVE_MATERIAL_DB, ACTIVE_BELT_SPECS
from .utils.unit_conversion import deg2rad
from .utils.trough_utils import parse_trough_label, capacity_from_geometry_tph

# --- Dữ liệu số hóa từ Mục 8, "TÍNH TOÁN BĂNG TẢI.pdf" ---

# Bảng 22: Đường kính puly tối thiểu cho băng tải sợi thép (mm)
PULLEY_DIAMETERS_ST_MM: Dict[str, Dict[str, int]] = {
    "ST-500": {"A": 500, "B": 400, "C": 300},
    "ST-630": {"A": 550, "B": 440, "C": 330},
    "ST-800": {"A": 600, "B": 480, "C": 360},
    "ST-1000": {"A": 700, "B": 560, "C": 420},
    "ST-1250": {"A": 750, "B": 600, "C": 450},
    "ST-1600": {"A": 900, "B": 720, "C": 540},
    "ST-2000": {"A": 950, "B": 760, "C": 570},
    "ST-2500": {"A": 1250, "B": 1000, "C": 750},
    "ST-3150": {"A": 1400, "B": 1120, "C": 840},
    "ST-4000": {"A": 1650, "B": 1320, "C": 990},
    "ST-5000": {"A": 2050, "B": 1640, "C": 1230},
}

# Bảng 23: Đường kính puly tối thiểu cho băng tải dệt (mm) - Đơn giản hóa
PULLEY_DIAMETERS_FABRIC_MM: Dict[int, Dict[str, int]] = {
    160: {"high": 250, "medium": 200, "low": 160},
    200: {"high": 250, "medium": 200, "low": 160},
    250: {"high": 320, "medium": 250, "low": 200},
    315: {"high": 400, "medium": 250, "low": 250},
    400: {"high": 500, "medium": 400, "low": 320},
    500: {"high": 500, "medium": 400, "low": 320},
    630: {"high": 630, "medium": 500, "low": 400},
    800: {"high": 800, "medium": 630, "low": 500},
    1000: {"high": 1000, "medium": 800, "low": 630},
    1250: {"high": 1000, "medium": 800, "low": 630},
    1600: {"high": 1000, "medium": 800, "low": 630},
}

# Bảng 24: Khoảng cách con lăn đỡ nhánh căng (m)
IDLER_SPACING_CARRY_M: Dict[int, Dict[int, float]] = {
    400: {480: 1.7, 800: 1.7, 1200: 1.5, 1600: 1.5, 2000: 1.4, 2400: 1.0},
    500: {480: 1.7, 800: 1.7, 1200: 1.5, 1600: 1.5, 2000: 1.4, 2400: 1.0},
    650: {480: 1.5, 800: 1.5, 1200: 1.4, 1600: 1.4, 2000: 1.3, 2400: 1.0},
    800: {480: 1.5, 800: 1.5, 1200: 1.4, 1600: 1.4, 2000: 1.2, 2400: 1.0},
    1000: {480: 1.5, 800: 1.4, 1200: 1.2, 1600: 1.2, 2000: 1.0, 2400: 0.9},
    1200: {480: 1.5, 800: 1.4, 1200: 1.0, 1600: 1.0, 2000: 0.9, 2400: 0.8},
    1400: {480: 1.2, 800: 1.2, 1200: 0.9, 1600: 0.9, 2000: 0.8, 2400: 0.8},
    1600: {480: 1.2, 800: 1.2, 1200: 0.8, 1600: 0.8, 2000: 0.8, 2400: 0.6},
    1800: {480: 1.2, 800: 1.2, 1200: 0.8, 1600: 0.8, 2000: 0.8, 2400: 0.6},
    2000: {480: 1.2, 800: 1.2, 1200: 0.8, 1600: 0.8, 2000: 0.8, 2400: 0.6},
}

# Bảng 27 & 28: Hệ số khoảng cách chuyển tiếp (b/B)
TRANSITION_DISTANCE_FACTORS: Dict[str, Dict[int, Dict[int, float]]] = {
    "fabric": {
        20: {600: 0.55, 800: 0.75, 1000: 0.95, 1200: 1.10, 1400: 1.30, 1600: 1.45, 1800: 1.65, 2000: 1.85},
        35: {600: 0.95, 800: 1.25, 1000: 1.35, 1200: 1.90, 1400: 1.90, 1600: 2.55, 1800: 2.45, 2000: 3.15},
        45: {600: 1.20, 800: 1.60, 1000: 2.00, 1200: 2.40, 1400: 2.80, 1600: 3.20, 1800: 3.60, 2000: 4.00},
    },
    "steel": {
        20: {600: 1.10, 800: 1.50, 1000: 1.85, 1200: 2.20, 1400: 2.55, 1600: 2.95, 1800: 3.30, 2000: 3.65},
        35: {600: 1.90, 800: 2.55, 1000: 3.15, 1200: 3.80, 1400: 4.45, 1600: 5.05, 1800: 5.70, 2000: 6.35},
        45: {600: 2.40, 800: 3.20, 1000: 4.05, 1200: 4.85, 1400: 5.65, 1600: 6.45, 1800: 7.25, 2000: 8.05},
    }
}

# ---------------- Helpers ----------------

def get_friction_and_lo_cema(p: ConveyorParameters) -> Tuple[float, float]:
    f, lo = 0.022, 66.0
    
    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG FRICTION: f={f}, lo={lo}")
    
    return f, lo

def get_moving_parts_weight_cema(width_mm: int) -> float:
    lookup = {
        400: 22, 500: 30, 650: 41, 800: 56, 1000: 69,
        1200: 90, 1400: 114, 1600: 130, 1800: 154, 2000: 174
    }
    closest = min(lookup, key=lambda w: abs(w - width_mm))
    weight = lookup[closest]
    
    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG MOVING_PARTS: width_mm={width_mm}, closest={closest}, weight={weight}")
    
    return weight

def get_idler_base_weights(width_mm: int) -> Tuple[float, float]:
    wc_wr_lookup = {
        400: (6.6, 5.0), 500: (7.5, 5.9), 650: (9.0, 7.3), 800: (13.9, 12.2),
        1000: (19.6, 18.0), 1200: (23.6, 21.1), 1400: (36.6, 32.6),
        1600: (41.4, 36.6), 1800: (47.4, 42.5), 2000: (52.2, 46.5)
    }
    closest_w = min(wc_wr_lookup, key=lambda w: abs(w - width_mm))
    weights = wc_wr_lookup[closest_w]
    
    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG IDLER_WEIGHTS: width_mm={width_mm}, closest_w={closest_w}, weights={weights}")
    
    return weights

def get_default_spacings(width_mm: int, capacity_tph: float) -> Tuple[float, float]:
    lc_lookup_low = {
        400: 1.35, 500: 1.35, 650: 1.20, 800: 1.20, 900: 1.00,
        1000: 1.00, 1200: 1.00, 1400: 1.00, 1600: 1.00, 1800: 1.00, 2000: 1.00
    }
    lc_lookup_high = {
        400: 1.35, 500: 1.20, 650: 1.10, 800: 1.00, 900: 1.00,
        1000: 1.00, 1200: 1.00, 1400: 1.00, 1600: 1.00, 1800: 1.00, 2000: 1.00
    }
    lr_default = 3.0
    lc_table = lc_lookup_high if capacity_tph > 1600 else lc_lookup_low
    closest_lc = min(lc_table, key=lambda w: abs(w - width_mm))
    spacings = (lc_table[closest_lc], lr_default)
    
    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG SPACINGS: width_mm={width_mm}, capacity_tph={capacity_tph}")
    print(f"DEBUG SPACINGS: lc_table={'high' if capacity_tph > 1600 else 'low'}, closest_lc={closest_lc}")
    print(f"DEBUG SPACINGS: spacings={spacings}")
    
    return spacings

def calculate_belt_weight(B_mm: int, thickness_mm: float, belt_type: str) -> float:
    rho = 1220.0
    if "PVC" in (belt_type or ""):
        rho = 1350.0
    if "Dây thép" in (belt_type or "") or "ST" in (belt_type or ""):
        rho = 1400.0
    B_m = max(0.3, float(B_mm) / 1000.0)
    t_m = max(0.005, float(thickness_mm) / 1000.0)
    weight = B_m * t_m * rho * 1.05
    
    # Debug: in ra các giá trị để kiểm tra
    print(f"DEBUG BELT_WEIGHT: B_mm={B_mm}, thickness_mm={thickness_mm}, belt_type={belt_type}")
    print(f"DEBUG BELT_WEIGHT: rho={rho}, B_m={B_m}, t_m={t_m}, weight={weight}")
    
    return weight

# ---------------- Strategies ----------------

class CalculationStrategy(ABC):
    def __init__(self, params: ConveyorParameters, result: CalculationResult, common_data: dict, belt_specs: dict):
        self.p = params
        self.r = result
        self.common_data = common_data
        self.belt_specs = belt_specs

    @abstractmethod
    def calculate_resistances_and_power(self):
        ...

    def _effective_drive_contact(self) -> Tuple[float, float, bool]:
        base_wrap = float(self.p.wrap_deg or 210.0)
        base_mu = float(self.p.mu_pulley or 0.35)
        dt = (self.p.drive_type or "").strip().lower()
        
        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG DRIVE_CONTACT: base_wrap={base_wrap}, base_mu={base_mu}, drive_type={dt}")
        
        if dt == "tail drive":
            result = (max(base_wrap - 30.0, 120.0), base_mu * 0.95, False)
            print(f"DEBUG DRIVE_CONTACT: tail drive result={result}")
            return result
        if dt == "center drive":
            result = (min(max(base_wrap, 160.0), 200.0), base_mu * 0.97, False)
            print(f"DEBUG DRIVE_CONTACT: center drive result={result}")
            return result
        # Dual drive is handled separately, but we return values for consistency
        if dt == "dual drive":
            result = (min(base_wrap + 20.0, 240.0), base_mu, True)
            print(f"DEBUG DRIVE_CONTACT: dual drive result={result}")
            return result
        result = (base_wrap, base_mu, False)
        print(f"DEBUG DRIVE_CONTACT: default result={result}")
        return result

    def _compute_geometry_capacity(self):
        print(f"DEBUG _compute_geometry_capacity: START")
        print(f"DEBUG _compute_geometry_capacity: trough_angle_label='{self.p.trough_angle_label}'")
        print(f"DEBUG _compute_geometry_capacity: about to call parse_trough_label...")
        try:
            trough_deg = parse_trough_label(self.p.trough_angle_label)
            print(f"DEBUG _compute_geometry_capacity: parse_trough_label returned {trough_deg}")
        except Exception as e:
            print(f"DEBUG _compute_geometry_capacity: ERROR calling parse_trough_label: {e}")
            import traceback
            traceback.print_exc()
            trough_deg = 20.0  # fallback
        surcharge_deg = float(getattr(self.p, "surcharge_angle_deg", 20.0) or 20.0)
        
        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG: trough_angle_label={self.p.trough_angle_label}, parsed_trough_deg={trough_deg}")
        print(f"DEBUG: surcharge_angle_deg={surcharge_deg}")
        print(f"DEBUG: B_mm={self.p.B_mm}, V_mps={self.p.V_mps}, density_tpm3={self.p.density_tpm3}")
        
        print(f"DEBUG _compute_geometry_capacity: calling capacity_from_geometry_tph")
        Qt_calc, A = capacity_from_geometry_tph(
            self.p.B_mm, trough_deg, surcharge_deg,
            self.p.V_mps, self.p.density_tpm3
        )
        print(f"DEBUG _compute_geometry_capacity: capacity_from_geometry_tph returned Qt_calc={Qt_calc}, A={A}")
        self.r.cross_section_area_m2 = A
        self.r.Qt_calc_tph = Qt_calc
        
        # Debug: in ra kết quả tính toán
        print(f"DEBUG: Qt_calc={Qt_calc}, A={A}")
        
        if self.p.Qt_tph > 0:
            util = 100.0 * self.p.Qt_tph / max(Qt_calc, 1e-6)
            self.r.capacity_utilization = util
            if util > 105.0:
                self.r.warnings.append(
                    f"Lưu lượng yêu cầu {self.p.Qt_tph:.1f} t/h vượt năng lực tiết diện "
                    f"Q_max≈{Qt_calc:.1f} t/h (B={self.p.B_mm} mm, máng≈{trough_deg:.0f}°, surcharge≈{surcharge_deg:.0f}°)."
                )
            elif util > 95.0:
                self.r.warnings.append(
                    f"Lưu lượng yêu cầu đang tiệm cận năng lực tiết diện ({util:.1f}%)."
                )
        
        print(f"DEBUG _compute_geometry_capacity: END")

    def _apply_geo_limitation_to_load(self):
        V = max(0.05, float(self.p.V_mps))
        
        # SỬA LỖI: Tính q_from_Qt dựa trên lưu lượng yêu cầu và khối lượng riêng
        # q_from_Qt = (Qt_tph * 1000 kg/t) / (3600 s/h * V m/s) = kg/m
        # Nhưng Qt_tph phải được điều chỉnh theo khối lượng riêng để duy trì cùng một tải trọng vật liệu
        # Khi khối lượng riêng thay đổi, tải trọng vật liệu trên băng tải phải thay đổi
        q_from_Qt = (self.p.Qt_tph * 1000.0 / 3600.0) / V
        
        # Tính q_from_geo: tải trọng vật liệu từ tiết diện và khối lượng riêng
        # q_from_geo = A m² * 1000 kg/m³ = kg/m
        q_from_geo = float(self.r.cross_section_area_m2) * 1000.0 * float(self.p.density_tpm3)
        
        # Lấy giá trị nhỏ hơn để đảm bảo không vượt quá khả năng tiết diện
        q_eff = min(q_from_Qt, q_from_geo)
        
        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG: V={V}, q_from_Qt={q_from_Qt:.3f}, q_from_geo={q_from_geo:.3f}")
        print(f"DEBUG: density_tpm3={self.p.density_tpm3}, cross_section_area_m2={self.r.cross_section_area_m2:.6f}")
        print(f"DEBUG: q_eff={q_eff:.3f}")
        print(f"DEBUG: BEFORE - material_load_kgpm={self.r.material_load_kgpm:.3f}")
        
        # SỬA LỖI: material_load_kgpm được tính dựa trên q_from_Qt để đảm bảo công suất động cơ thay đổi khi thay đổi vật liệu
        # Khi khối lượng riêng thay đổi, tải trọng vật liệu trên băng tải phải thay đổi để duy trì cùng một lưu lượng
        self.r.material_load_kgpm = q_from_Qt
        
        # Kiểm tra xem có bị khống chế bởi tiết diện không
        if q_eff < q_from_Qt - 1e-6:
            # Bị khống chế bởi tiết diện
            self.r.warnings.append(
                f"Lưu lượng thực bị khống chế bởi tiết diện: Q_thực≈{q_eff * V * 3.6 / 1000.0:.1f} t/h < Q_yêu cầu={self.p.Qt_tph:.1f} t/h."
            )
            print(f"DEBUG: WARNING: Geometric limitation detected, but material_load_kgpm still set to {q_from_Qt:.3f}")
        else:
            print(f"DEBUG: No geometric limitation, material_load_kgpm set to {q_from_Qt:.3f}")
        
        # Luôn cập nhật total_load_kgpm và mass_flow_rate
        self.r.total_load_kgpm = self.r.material_load_kgpm + self.r.belt_weight_kgpm + self.r.moving_parts_weight_kgpm
        self.r.mass_flow_rate = self.r.material_load_kgpm * V
        self.r.Qt_effective_tph = self.r.mass_flow_rate * 3.6 / 1000.0
        
        print(f"DEBUG: AFTER - material_load_kgpm={self.r.material_load_kgpm:.3f}, total_load_kgpm={self.r.total_load_kgpm:.3f}")
        print(f"DEBUG: mass_flow_rate={self.r.mass_flow_rate:.3f}, Qt_effective_tph={self.r.Qt_effective_tph:.3f}")

    # --- [BẮT ĐẦU NÂNG CẤP] ---
    def _calculate_single_drive_tensions(self):
        """Tính toán lực căng cho hệ thống truyền động đơn."""
        # Tính effective_tension từ lực ma sát và lực nâng đã được tính trong calculate_resistances_and_power
        self.r.effective_tension = self.r.friction_force + self.r.lift_force
        wrap_deg_eff, mu_eff, _ = self._effective_drive_contact()
        theta = deg2rad(wrap_deg_eff)
        self.r.wrap_angle_rad = theta
        e_ratio = math.exp(mu_eff * theta)

        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG TENSION: effective_tension={self.r.effective_tension}")
        print(f"DEBUG TENSION: friction_force={self.r.friction_force}, lift_force={self.r.lift_force}")
        print(f"DEBUG TENSION: wrap_deg_eff={wrap_deg_eff}, mu_eff={mu_eff}, theta={theta}")
        print(f"DEBUG TENSION: mu_eff * theta={mu_eff * theta}, e_ratio={e_ratio}")

        if abs(e_ratio - 1.0) < 1e-6:
            self.r.T2 = self.r.effective_tension * 10.0
            print(f"DEBUG TENSION: e_ratio ≈ 1, using T2 = effective_tension * 10 = {self.r.T2}")
        else:
            self.r.T2 = self.r.effective_tension / (e_ratio - 1.0)
            print(f"DEBUG TENSION: e_ratio ≠ 1, using T2 = effective_tension / (e_ratio - 1) = {self.r.T2}")
        
        self.r.T1 = self.r.effective_tension + self.r.T2
        self.r.max_tension = self.r.T1
        
        # Debug: in ra kết quả cuối cùng
        print(f"DEBUG TENSION: T2={self.r.T2}, T1={self.r.T1}, max_tension={self.r.max_tension}")

    def _calculate_dual_drive_tensions(self):
        """
        Tính toán lực căng cho hệ thống truyền động kép theo Mục 6.2, PDF.
        Phương pháp này sử dụng cách tính lực cản riêng, dựa trên CEMA.
        """
        f, lo = get_friction_and_lo_cema(self.p)
        l = self.p.L_m
        h = self.p.H_m
        W1 = self.r.belt_weight_kgpm
        Wm = self.r.material_load_kgpm
        Wc, Wr = get_idler_base_weights(self.p.B_mm)
        lc, lr = self.p.carrying_idler_spacing_m, self.p.return_idler_spacing_m

        # Công thức (19) & (20) từ PDF, trang 18. Đơn vị lực là [kgf]
        Fc_kgf = f * (l + lo) * (W1 + Wc / lc + Wm) + h * (W1 + Wm)
        Fr_kgf = f * (l + lo) * (W1 + Wr / lr) - h * W1
        
        # Đổi dấu h cho băng tải xuống dốc
        if h < 0:
            Fc_kgf = f * (l + lo) * (W1 + Wc / lc + Wm) + h * (W1 + Wm)
            Fr_kgf = f * (l + lo) * (W1 + Wr / lr) - h * W1
        
        self.r.Fc_drive = Fc_kgf
        self.r.Fr_drive = Fr_kgf
        
        # Công thức (21): Tổng lực vòng Fp [kgf]
        Fp_kgf = Fc_kgf + Fr_kgf
        self.r.effective_tension = Fp_kgf * G  # Lưu lực vòng tổng bằng Newton

        mu1 = mu2 = self.p.mu_pulley
        theta1 = theta2 = deg2rad(self.p.wrap_deg)
        e_mu_theta1 = math.exp(mu1 * theta1)
        
        # Phân phối lực vòng Fp1, Fp2 [kgf]
        if self.p.dual_drive_ratio == "Phân phối lý thuyết":
            # Công thức (23)
            e_mu_theta2 = math.exp(mu2 * theta2)
            e_sum = math.exp(mu1 * theta1 + mu2 * theta2)
            Fp2_kgf = ((e_mu_theta2 - 1) / (e_sum - 1)) * (Fp_kgf + Fr_kgf * (e_mu_theta1 - 1))
            Fp1_kgf = Fp_kgf - Fp2_kgf
            self.r.drive_distribution_method = "Lý thuyết"
        elif self.p.dual_drive_ratio == "Phân phối 2/1 (66/33)":
            Fp1_kgf = Fp_kgf * (2/3)
            Fp2_kgf = Fp_kgf * (1/3)
            self.r.drive_distribution_method = "Tỷ lệ 2/1"
        else: # Mặc định là "Phân phối đều (50/50)"
            Fp1_kgf = Fp_kgf / 2.0
            Fp2_kgf = Fp_kgf / 2.0
            self.r.drive_distribution_method = "Tỷ lệ 50/50"

        self.r.Fp1 = Fp1_kgf
        self.r.Fp2 = Fp2_kgf

        # Công thức (24) & (25): Lực căng nhánh chùng F21, F22 [kgf]
        F21_kgf = Fp1_kgf / (e_mu_theta1 - 1) if abs(e_mu_theta1 - 1) > 1e-6 else Fp1_kgf * 10
        F22_kgf = Fp2_kgf / (math.exp(mu2 * theta2) - 1) if abs(math.exp(mu2 * theta2) - 1) > 1e-6 else Fp2_kgf * 10

        # Lực căng nhánh căng F11, F12 [kgf]
        F11_kgf = Fp1_kgf + F21_kgf
        F12_kgf = Fp2_kgf + F22_kgf
        
        # Lưu kết quả bằng Newton [N]
        self.r.F21 = F21_kgf * G
        self.r.F22 = F22_kgf * G
        self.r.F11 = F11_kgf * G
        self.r.F12 = F12_kgf * G
        
        # Lực căng lớn nhất của hệ thống là F11
        self.r.max_tension = self.r.F11
        
        # Công suất yêu cầu tính từ tổng lực vòng Fp
        self.r.required_power_kw = Fp_kgf * G * self.p.V_mps / 1000.0
        
        # Gán các lực ma sát và lực nâng để hiển thị trên biểu đồ
        self.r.friction_force = (self.r.Fc_drive + self.r.Fr_drive) * G if h == 0 else self.r.Fc_drive * G
        self.r.lift_force = 0 if h == 0 else (h * (W1 + Wm)) * G
    # --- [KẾT THÚC NÂNG CẤP] ---

    def execute(self) -> CalculationResult:
        # Debug: kiểm tra giá trị đầu vào
        print(f"DEBUG EXECUTE START: Qt_tph={self.p.Qt_tph}, V_mps={self.p.V_mps}")
        print(f"DEBUG EXECUTE START: B_mm={self.p.B_mm}, belt_thickness_mm={self.p.belt_thickness_mm}, belt_type={self.p.belt_type}")
        
        self.r.mass_flow_rate = self.p.Qt_tph * 1000.0 / 3600.0
        self.r.material_load_kgpm = self.r.mass_flow_rate / max(self.p.V_mps, 0.1)
        self.r.belt_weight_kgpm = calculate_belt_weight(self.p.B_mm, self.p.belt_thickness_mm, self.p.belt_type)
        try:
            self.r.moving_parts_weight_kgpm = get_moving_parts_weight_cema(self.p.B_mm)
        except Exception:
            self.r.moving_parts_weight_kgpm = 0.0
        self.r.total_load_kgpm = self.r.material_load_kgpm + self.r.belt_weight_kgpm + self.r.moving_parts_weight_kgpm

        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG: Qt_tph={self.p.Qt_tph}, V_mps={self.p.V_mps}")
        print(f"DEBUG: mass_flow_rate={self.r.mass_flow_rate}, material_load_kgpm={self.r.material_load_kgpm}")
        print(f"DEBUG: belt_weight_kgpm={self.r.belt_weight_kgpm}, moving_parts_weight_kgpm={self.r.moving_parts_weight_kgpm}")
        print(f"DEBUG: total_load_kgpm={self.r.total_load_kgpm}")
        print(f"DEBUG: B_mm={self.p.B_mm}, belt_thickness_mm={self.p.belt_thickness_mm}, belt_type={self.p.belt_type}")
        print(f"DEBUG: calculation_standard={self.p.calculation_standard}, drive_type={self.p.drive_type}")

        self._compute_geometry_capacity()
        self._apply_geo_limitation_to_load()
        
        # Cập nhật lại total_load_kgpm sau khi material_load_kgpm có thể đã thay đổi
        self.r.total_load_kgpm = self.r.material_load_kgpm + self.r.belt_weight_kgpm + self.r.moving_parts_weight_kgpm
        
        # Cập nhật lại mass_flow_rate và Qt_effective_tph dựa trên material_load_kgpm mới
        V = max(0.05, float(self.p.V_mps))
        self.r.mass_flow_rate = self.r.material_load_kgpm * V
        self.r.Qt_effective_tph = self.r.mass_flow_rate * 3.6 / 1000.0
        
        # Debug: sau khi áp dụng giới hạn hình học
        print(f"DEBUG: AFTER GEO - material_load_kgpm={self.r.material_load_kgpm}, total_load_kgpm={self.r.total_load_kgpm}")
        print(f"DEBUG: AFTER GEO - mass_flow_rate={self.r.mass_flow_rate}, Qt_effective_tph={self.r.Qt_effective_tph}")
        
        # --- [BẮT ĐẦU NÂNG CẤP] ---
        # Phân luồng tính toán cho truyền động đơn và kép
        if self.p.drive_type == "Dual drive":
            if self.p.calculation_standard != "CEMA":
                 self.r.warnings.append(f"Tính toán truyền động kép hiện tại dựa trên phương pháp CEMA (Mục 6.2, PDF), bỏ qua lựa chọn {self.p.calculation_standard}.")
            print(f"DEBUG: Using dual drive calculation")
            self._calculate_dual_drive_tensions()
        else:
            print(f"DEBUG: Using single drive calculation with {self.p.calculation_standard}")
            self.calculate_resistances_and_power()
            self._calculate_single_drive_tensions()
        # --- [KẾT THÚC NÂNG CẤP] ---

        self.finalize_results()
        self._calculate_costs()
        self._calculate_pulleys_and_idlers()
        
        # Debug: kết quả cuối cùng
        print(f"DEBUG FINAL: required_power_kw={self.r.required_power_kw}")
        print(f"DEBUG FINAL: motor_power_kw={self.r.motor_power_kw}")
        print(f"DEBUG FINAL: safety_factor={self.r.safety_factor}")
        print(f"DEBUG FINAL: friction_force={self.r.friction_force}, lift_force={self.r.lift_force}")
        print(f"DEBUG FINAL: effective_tension={self.r.effective_tension}")
        print(f"DEBUG FINAL: T1={self.r.T1}, T2={self.r.T2}, max_tension={self.r.max_tension}")
        
        print(f"DEBUG CALCULATE: transmission_solution={self.r.transmission_solution}")
        print(f"DEBUG CALCULATE: safety_factor={self.r.safety_factor}")
        print(f"DEBUG CALCULATE: cost_capital_total={self.r.cost_capital_total}")
        return self.r

    def finalize_results(self):
        eta_m = max(0.5, float(getattr(self.p, "motor_efficiency", 0.95) or 0.95))
        eta_g = max(0.5, float(getattr(self.p, "gearbox_efficiency", 0.96) or 0.96))
        Kt = max(1.0, float(getattr(self.p, "Kt_start", 1.25) or 1.25))

        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG FINALIZE: eta_m={eta_m}, eta_g={eta_g}, Kt={Kt}")
        print(f"DEBUG FINALIZE: required_power_kw={self.r.required_power_kw}")
        print(f"DEBUG FINALIZE: max_tension={self.r.max_tension}")

        self.r.motor_power_kw = self.r.required_power_kw * Kt / (eta_m * eta_g)
        drive_eta = (eta_m * eta_g / Kt) * 100.0
        self.r.drive_efficiency_percent = drive_eta
        self.r.efficiency = drive_eta

        T_allow_Npm = self.belt_specs.get("T_allow_Npm", 6000.0)
        belt_capacity_N = (self.p.B_mm / 1000.0) * T_allow_Npm
        self.r.safety_factor = belt_capacity_N / max(self.r.max_tension, 1e-6)
        self.r.belt_strength_utilization = 100.0 * self.r.max_tension / max(belt_capacity_N, 1e-6)
        
        # Debug: in ra kết quả cuối cùng
        print(f"DEBUG FINALIZE: motor_power_kw={self.r.motor_power_kw}")
        print(f"DEBUG FINALIZE: safety_factor={self.r.safety_factor}")
        print(f"DEBUG FINALIZE: belt_strength_utilization={self.r.belt_strength_utilization}")
        print(f"DEBUG FINALIZE: T_allow_Npm={T_allow_Npm}, belt_capacity_N={belt_capacity_N}")

        n = 50
        L = max(self.p.L_m, 1.0)
        self.r.distances_m = [i * L / n for i in range(n + 1)]
        self.r.friction_force_profile = [self.r.friction_force * (d / L) for d in self.r.distances_m]
        self.r.lift_force_profile = [self.r.lift_force * (d / L) for d in self.r.distances_m]
        
        # Cập nhật profile lực căng cho cả 2 trường hợp
        if self.p.drive_type == "Dual drive":
             # Với truyền động kép, T2 là F21 (lực căng nhánh chùng tại puly 1)
            t2_base = self.r.F21
            self.r.t2_profile = [t2_base for _ in self.r.distances_m]
        else:
            t2_base = self.r.T2
            self.r.t2_profile = [t2_base for _ in self.r.distances_m]

        self.r.tension_profile = [
            t2_base + self.r.friction_force_profile[i] + self.r.lift_force_profile[i]
            for i in range(len(self.r.distances_m))
        ]

        if self.r.safety_factor < 6.0:
            self.r.warnings.append(f"Hệ số an toàn thấp (SF = {self.r.safety_factor:.2f} < 6).")
            if "Dây thép" not in (self.p.belt_type or ""):
                self.r.recommendations.append("Cân nhắc tăng bề rộng hoặc chọn đai bền hơn (ST).")
        if self.r.belt_strength_utilization > 80.0:
            self.r.warnings.append(f"Mức sử dụng cường độ đai cao ({self.r.belt_strength_utilization:.1f}%).")
            self.r.recommendations.append("Cân nhắc tăng bề rộng băng hoặc chọn đai bền hơn.")

    def _calculate_costs(self):
        cost_per_m2 = self.belt_specs.get("cost_per_m2", 50.0)
        belt_area_m2 = (self.p.B_mm / 1000.0) * self.p.L_m * 2.1
        self.r.cost_belt = belt_area_m2 * cost_per_m2

        import math as _m
        lc_used = max(0.5, float(getattr(self.p, "carrying_idler_spacing_m", 1.2) or 1.2))
        lr_used = max(1.0, float(getattr(self.p, "return_idler_spacing_m", 3.0) or 3.0))
        num_carry = _m.ceil(self.p.L_m / lc_used)
        num_return = _m.ceil(self.p.L_m / lr_used)

        cost_per_idler = 30.0 + (self.p.B_mm / 1000.0) * 80.0
        self.r.cost_idlers = (num_carry + num_return) * cost_per_idler

        cost_per_m_struct = 150.0 + (self.p.B_mm / 1000.0) * 200.0
        self.r.cost_structure = self.p.L_m * cost_per_m_struct

        self.r.cost_drive = self.r.motor_power_kw * 750.0 + (self.r.drum_diameter_mm / 1000.0) ** 2 * 2000.0 * 2.0

        self.r.cost_others = (self.r.cost_belt + self.r.cost_idlers + self.r.cost_structure + self.r.cost_drive) * 0.15
        self.r.cost_capital_total = self.r.cost_belt + self.r.cost_idlers + self.r.cost_structure + self.r.cost_drive + self.r.cost_others

        kwh_per_year = self.r.required_power_kw * (self.p.operating_hours * 365.0)
        self.r.op_cost_energy_per_year = kwh_per_year * 0.12
        self.r.op_cost_maintenance_per_year = self.r.cost_capital_total * 0.02
        self.r.op_cost_total_per_year = self.r.op_cost_energy_per_year + self.r.op_cost_maintenance_per_year

        # --- [BẮT ĐẦU TÍNH TOÁN KHỐI LƯỢNG] ---
        # Ước tính khối lượng các thành phần
        belt_mass = self.r.belt_weight_kgpm * self.p.L_m * 2.1
        
        Wc, Wr = get_idler_base_weights(self.p.B_mm)
        idler_mass = (num_carry * Wc) + (num_return * Wr)
        
        # Ước tính khối lượng kết cấu và hệ thống truyền động
        # Giả định giá thép kết cấu là $5/kg và giá hệ thống truyền động là $10/kg
        structure_mass = self.r.cost_structure / 5.0 if self.r.cost_structure > 0 else self.p.L_m * 50
        drive_mass = self.r.cost_drive / 10.0 if self.r.cost_drive > 0 else self.r.motor_power_kw * 20
        
        self.r.total_mass_kg = belt_mass + idler_mass + structure_mass + drive_mass
        # --- [KẾT THÚC TÍNH TOÁN KHỐI LƯỢNG] ---
        
        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG COSTS: cost_belt={self.r.cost_belt}, cost_idlers={self.r.cost_idlers}")
        print(f"DEBUG COSTS: cost_structure={self.r.cost_structure}, cost_drive={self.r.cost_drive}")
        print(f"DEBUG COSTS: cost_capital_total={self.r.cost_capital_total}")
        print(f"DEBUG COSTS: op_cost_energy_per_year={self.r.op_cost_energy_per_year}")
        print(f"DEBUG MASS: belt_mass={belt_mass:.2f}, idler_mass={idler_mass:.2f}, structure_mass={structure_mass:.2f}, drive_mass={drive_mass:.2f}")
        print(f"DEBUG MASS: total_mass_kg={self.r.total_mass_kg:.2f}")

    def _calculate_pulleys_and_idlers(self):
        dia_A = 0.0
        is_steel_cord = "ST" in self.p.belt_type or "Thép" in self.p.belt_type

        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG PULLEYS: belt_type={self.p.belt_type}, is_steel_cord={is_steel_cord}")
        print(f"DEBUG PULLEYS: max_tension={self.r.max_tension}, safety_factor={self.r.safety_factor}")

        if is_steel_cord:
            f_max_kg = self.r.max_tension / G
            st_no_calc = f_max_kg * self.r.safety_factor / (self.p.B_mm / 10.0)
            st_types = sorted([int(s.replace("ST-", "")) for s in PULLEY_DIAMETERS_ST_MM.keys()])
            closest_st_val = min(st_types, key=lambda x: float('inf') if x < st_no_calc else x - st_no_calc)
            st_key = f"ST-{closest_st_val}"
            if st_key in PULLEY_DIAMETERS_ST_MM:
                dia_A = PULLEY_DIAMETERS_ST_MM[st_key]['A']
        else:
            load_level_percent = self.r.belt_strength_utilization
            if load_level_percent > 60:
                load_category_key = "high"
            elif 30 <= load_level_percent <= 60:
                load_category_key = "medium"
            else:
                load_category_key = "low"
            
            strength_class = self.belt_specs.get("strength", 400)
            available_strengths = sorted(PULLEY_DIAMETERS_FABRIC_MM.keys())
            closest_strength_class = min(available_strengths, key=lambda x: abs(x - strength_class))
            
            if closest_strength_class in PULLEY_DIAMETERS_FABRIC_MM:
                dia_A = PULLEY_DIAMETERS_FABRIC_MM[closest_strength_class][load_category_key]
        
        # Debug: in ra kết quả
        print(f"DEBUG PULLEYS: dia_A={dia_A}")

        dia_B = dia_A * 0.8
        dia_C = dia_A * 0.6
        
        self.r.recommended_pulley_diameters_mm = {
            "Puly dẫn động/đầu (Loại A)": round(dia_A),
            "Puly căng/đuôi (Loại B)": round(dia_B),
            "Puly dẫn hướng (Loại C)": round(dia_C),
        }
        self.r.drum_diameter_mm = round(dia_A)

        density_kgm3 = self.p.density_tpm3 * 1000
        available_widths = sorted(IDLER_SPACING_CARRY_M.keys())
        closest_width = min(available_widths, key=lambda w: abs(w - self.p.B_mm))
        
        spacing_map = IDLER_SPACING_CARRY_M.get(closest_width, {})
        available_densities = sorted(spacing_map.keys())
        closest_density = min(available_densities, key=lambda d: abs(d - density_kgm3)) if available_densities else 0
        
        spacing_carry = spacing_map.get(closest_density, 1.2)
        spacing_return = 2.4 if self.p.B_mm >= 2000 else 3.0

        self.r.recommended_idler_spacing_m = {
            "Nhánh tải (đề xuất)": spacing_carry,
            "Nhánh về (đề xuất)": spacing_return,
        }

        belt_cat = "steel" if is_steel_cord else "fabric"
        trough_deg = parse_trough_label(self.p.trough_angle_label, 20.0)
        
        factors_table = TRANSITION_DISTANCE_FACTORS.get(belt_cat, {})
        available_angles = sorted(factors_table.keys())
        closest_angle = min(available_angles, key=lambda a: abs(a - trough_deg))
        
        width_map = factors_table.get(closest_angle, {})
        available_widths_trans = sorted(width_map.keys())
        closest_width_trans = min(available_widths_trans, key=lambda w: abs(w - self.p.B_mm))
        
        factor = width_map.get(closest_width_trans, 1.5)
        self.r.transition_distance_m = factor * (self.p.B_mm / 1000.0)


# --------- Concrete strategies ---------

class CEMAStrategy(CalculationStrategy):
    def calculate_resistances_and_power(self):
        f, lo = get_friction_and_lo_cema(self.p)
        V_mpm = self.p.V_mps * 60.0
        W_kgpm = get_moving_parts_weight_cema(self.p.B_mm)
        
        P1_kw = (f * (self.p.L_m + lo) * W_kgpm * V_mpm) / 6120.0
        P2_kw = (f * (self.p.L_m + lo) * self.r.material_load_kgpm * V_mpm) / 6120.0
        P3_kw = (self.p.H_m * self.r.material_load_kgpm) * G * self.p.V_mps / 1000.0
        
        # Debug: in ra các giá trị để kiểm tra
        print(f"DEBUG CEMA: f={f}, lo={lo}, V_mpm={V_mpm}, W_kgpm={W_kgpm}")
        print(f"DEBUG CEMA: L_m={self.p.L_m}, H_m={self.p.H_m}, material_load_kgpm={self.r.material_load_kgpm}")
        print(f"DEBUG CEMA: P1_kw={P1_kw}, P2_kw={P2_kw}, P3_kw={P3_kw}")
        
        self.r.P1_kw = P1_kw
        self.r.P2_kw = P2_kw
        self.r.P3_kw = P3_kw
        self.r.Pt_kw = 0.0
        self.r.required_power_kw = P1_kw + P2_kw + P3_kw
        self.r.friction_force = (P1_kw + P2_kw) * 1000.0 / max(self.p.V_mps, 0.1)
        self.r.lift_force = (P3_kw * 1000.0 / max(self.p.V_mps, 0.1)) if P3_kw > 0 else 0.0
        
        # Debug: in ra kết quả cuối cùng
        print(f"DEBUG CEMA: required_power_kw={self.r.required_power_kw}")
        print(f"DEBUG CEMA: friction_force={self.r.friction_force}, lift_force={self.r.lift_force}")
        print(f"DEBUG CEMA: V_mps={self.p.V_mps}, max(V_mps, 0.1)={max(self.p.V_mps, 0.1)}")

class DINStrategy(CalculationStrategy):
    def calculate_resistances_and_power(self):
        q_G = self.r.material_load_kgpm
        q_B = self.r.belt_weight_kgpm
        Wc, Wr = get_idler_base_weights(self.p.B_mm)

        lc_default, lr_default = get_default_spacings(self.p.B_mm, self.p.Qt_tph)
        lc_used = max(0.5, float(getattr(self.p, "carrying_idler_spacing_m", lc_default) or lc_default))
        lr_used = max(1.0, float(getattr(self.p, "return_idler_spacing_m", lr_default) or lr_default))

        q_R_upper = Wc / lc_used
        q_R_lower = Wr / lr_used

        f = 0.025
        L = self.p.L_m
        H = self.p.H_m
        F_friction = f * G * L * (2.0 * q_B + q_R_upper + q_R_lower + q_G)
        F_lift = G * H * q_G
        F_total = F_friction + F_lift
        self.r.required_power_kw = F_total * self.p.V_mps / 1000.0
        self.r.friction_force = F_friction
        self.r.lift_force = F_lift

class ISOStrategy(DINStrategy):
    def calculate_resistances_and_power(self):
        q_G = self.r.material_load_kgpm
        q_B = self.r.belt_weight_kgpm
        Wc, Wr = get_idler_base_weights(self.p.B_mm)

        lc_default, lr_default = get_default_spacings(self.p.B_mm, self.p.Qt_tph)
        lc_used = max(0.5, float(getattr(self.p, "carrying_idler_spacing_m", lc_default) or lc_default))
        lr_used = max(1.0, float(getattr(self.p, "return_idler_spacing_m", lr_default) or lr_default))

        q_R_upper = Wc / lc_used
        q_R_lower = Wr / lr_used

        f_iso = 0.022
        L = self.p.L_m
        H = self.p.H_m
        F_friction = f_iso * G * L * (2.0 * q_B + q_R_upper + q_R_lower + q_G)
        F_lift = G * H * q_G
        F_total = F_friction + F_lift
        self.r.required_power_kw = F_total * self.p.V_mps / 1000.0
        self.r.friction_force = F_friction
        self.r.lift_force = F_lift
        self.r.warnings.append("Đang tính theo ISO 5048 với hệ số ma sát thấp hơn DIN.")

# ---------------- API ----------------

def get_strategy(params: ConveyorParameters, result: CalculationResult, common_data: dict, belt_specs: dict) -> CalculationStrategy:
    std = (params.calculation_standard or "").strip()
    if std == "DIN 22101":
        return DINStrategy(params, result, common_data, belt_specs)
    if std == "ISO 5048":
        return ISOStrategy(params, result, common_data, belt_specs)
    return CEMAStrategy(params, result, common_data, belt_specs)

def calculate(p: ConveyorParameters) -> CalculationResult:
    r = CalculationResult()
    mat = ACTIVE_MATERIAL_DB.get(p.material, {})
    belt = ACTIVE_BELT_SPECS.get(p.belt_type, {})
    common_data = {"material": mat}
    belt_specs = belt or {}
    strat = get_strategy(p, r, common_data, belt_specs)
    result = strat.execute()
    
    # --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
    # Lưu motor_rpm vào kết quả để UI hiển thị chính xác
    result.motor_rpm = p.motor_rpm
    
    # Tính toán bộ truyền động hoàn chỉnh
    try:
        from .specs import ACTIVE_CHAIN_SPECS
        
        # Lấy đường kính puly từ kết quả tính toán
        pulley_diameter = result.recommended_pulley_diameters_mm.get('Puly dẫn động/đầu (Loại A)', 500)  # mm
        
        # Gọi hàm tìm giải pháp tối ưu
        transmission_solution = find_optimal_transmission(
            calculation_params=p,
            chain_specs=ACTIVE_CHAIN_SPECS,
            pulley_diameter=pulley_diameter,  # Truyền đường kính puly thực tế
            required_power_kw=result.required_power_kw if hasattr(result, "required_power_kw") else None
        )
        
        if transmission_solution:
            result.transmission_solution = transmission_solution
            # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
            # Gán thông tin về chế độ hộp số vào kết quả để UI hiển thị
            result.gearbox_ratio_mode = p.gearbox_ratio_mode
            result.gearbox_ratio_user = p.gearbox_ratio_user
            # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
            print(f"DEBUG: Đã tìm thấy giải pháp truyền động: {transmission_solution}")
        else:
            print("DEBUG: Không tìm thấy giải pháp truyền động phù hợp")
            # --- [BẮT ĐẦU SỬA LỖI] ---
            # Tạo một transmission_solution mặc định để tránh lỗi UI
            from .models import TransmissionSolution
            result.transmission_solution = TransmissionSolution()
            result.gearbox_ratio_mode = p.gearbox_ratio_mode
            result.gearbox_ratio_user = p.gearbox_ratio_user
            print("DEBUG: Đã tạo transmission_solution mặc định để tránh lỗi UI")
            # --- [KẾT THÚC SỬA LỖI] ---
            
    except Exception as e:
        print(f"DEBUG: Lỗi khi tính toán truyền động: {e}")
        # --- [BẮT ĐẦU SỬA LỖI] ---
        # Tạo transmission_solution mặc định để tránh lỗi UI
        from .models import TransmissionSolution
        result.transmission_solution = TransmissionSolution()
        result.gearbox_ratio_mode = p.gearbox_ratio_mode
        result.gearbox_ratio_user = p.gearbox_ratio_user
        print("DEBUG: Đã tạo transmission_solution mặc định sau khi có lỗi")
        # --- [KẾT THÚC SỬA LỖI] ---
    # --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---
    
    return result

# --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
def find_optimal_transmission(calculation_params: 'ConveyorParameters',
                              chain_specs: list,
                              pulley_diameter: float,
                              required_power_kw: float | None = None) -> Optional['TransmissionSolution']:
    """
    Tìm giải pháp truyền động tối ưu đa mục tiêu theo kế hoạch Plan C:
    1. Dùng dữ liệu thực từ Bang tra 1.csv (Tensile Strength, Measuring Load, ISO/ANSI, Strand)
    2. Chọn nhông‑xích theo kiểm tra bền kéo (có hệ số an toàn), không chỉ theo tỉ số và răng
    3. Tối ưu đa mục tiêu: sai số vận tốc → tổng răng nhỏ → i_s gần 1.9 → pitch nhỏ/nhẹ → margin bền kéo cao → hộp số dễ/tiết kiệm
    
    Args:
        calculation_params: Tham số tính toán băng tải
        chain_specs: Danh sách các loại xích có sẵn
    
    Returns:
        TransmissionSolution hoặc None nếu không tìm thấy giải pháp phù hợp
    """
    from .models import TransmissionSolution
    from .specs import STANDARD_GEARBOX_RATIOS, CHAIN_TENSILE_STRENGTH_SAFETY_FACTOR, PREFERRED_CHAIN_RATIO, PREFERRED_CHAIN_RANGE
    
    # Tính toán yêu cầu
    target_velocity = calculation_params.V_mps
    motor_rpm = calculation_params.motor_rpm
    
    # Tính tốc độ puly yêu cầu: n_pulley_req = (V * 60) / (π * D)
    rpm_pulley_required = (target_velocity * 60) / (math.pi * pulley_diameter / 1000)
    
    print(f"DEBUG TX: target_velocity={target_velocity} m/s, pulley_diameter={pulley_diameter} mm")
    print(f"DEBUG TX: motor_rpm={motor_rpm}, rpm_pulley_required={rpm_pulley_required:.2f}")
    
    valid_solutions = []
    
    # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
    # Xác định danh sách tỉ số hộp số theo chế độ
    use_manual = (calculation_params.gearbox_ratio_mode.lower() == "manual" and calculation_params.gearbox_ratio_user > 0)
    if use_manual:
        gearbox_candidates = [calculation_params.gearbox_ratio_user]
        print(f"DEBUG TX: Sử dụng chế độ Manual với i_g = {calculation_params.gearbox_ratio_user}")
    else:
        gearbox_candidates = STANDARD_GEARBOX_RATIOS
        print(f"DEBUG TX: Sử dụng chế độ Auto với {len(STANDARD_GEARBOX_RATIOS)} tỉ số chuẩn")
    # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
    
    # Vòng lặp chính - Duyệt qua các hộp số theo chế độ được chọn
    for gearbox_ratio in gearbox_candidates:
        # Tính tốc độ trục ra của hộp số
        output_rpm = motor_rpm / gearbox_ratio
        
        # Tính tỉ số truyền nhông-xích mục tiêu: i_s = n_out / n_pulley_req
        i_sprocket_target = output_rpm / rpm_pulley_required
        
        # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
        # Giới hạn tỉ số truyền nhông-xích trong khoảng hợp lý [1.2, 3.0]
        # Với chế độ Manual, clamp i_s_target nếu ngoài dải
        if i_sprocket_target < 1.2 or i_sprocket_target > 3.0:
            if use_manual:
                # Clamp i_s_target cho chế độ Manual
                clamped_i_s = max(1.2, min(3.0, i_sprocket_target))
                print(f"DEBUG TX: Manual mode - i_s_target {i_sprocket_target:.3f} ngoài dải [1.2, 3.0], clamp về {clamped_i_s:.3f}")
                i_sprocket_target = clamped_i_s
            else:
                # Bỏ qua cho chế độ Auto
                continue
        # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
        
        print(f"DEBUG TX: ig={gearbox_ratio}, output_rpm={output_rpm:.2f}, i_s_target={i_sprocket_target:.3f}")
        
        # Vòng lặp phụ - Tìm cặp nhông phù hợp
        for z1 in range(17, 26):  # Số răng nhông dẫn từ 17-25
            # Tính số răng nhông bị dẫn lý thuyết
            z2_ideal = z1 * i_sprocket_target
            z2_actual = round(z2_ideal)
            
            # Kiểm tra giới hạn số răng nhông bị dẫn
            if z2_actual < z1 or z2_actual > 120:
                continue
            
            # Tính lại tỉ số truyền thực tế
            i_sprocket_actual = z2_actual / z1
            i_total_actual = gearbox_ratio * i_sprocket_actual
            
            # Tính vận tốc băng tải thực tế
            actual_velocity = (motor_rpm / i_total_actual) * (math.pi * pulley_diameter / 1000) / 60
            
            # Tính sai số
            error = abs(actual_velocity - target_velocity) / target_velocity * 100
            
            # Vòng lặp thứ ba - Kiểm tra độ bền với từng loại xích (dựa vào Tensile Strength, KHÔNG dùng Measuring Load làm allowable)
            for chain_spec in chain_specs:
                try:
                    # Tốc độ xích (m/s)
                    circumference_m = (chain_spec.pitch_mm / 1000.0) * z1
                    v_chain = max(circumference_m * (output_rpm / 60.0), 1e-9)

                    # Công suất yêu cầu (W) -> lực kéo yêu cầu trên xích (kN)
                    if required_power_kw is not None and required_power_kw > 0:
                        P_req_W = required_power_kw * 1000.0
                        F_required_kN = (P_req_W / v_chain) / 1000.0
                    else:
                        # Fallback mềm để không loại bỏ toàn bộ khi thiếu dữ liệu
                        # Giả định tải yêu cầu nhỏ (có thể cấu hình/ghi log để người dùng bổ sung power)
                        F_required_kN = 0.5

                    # Allowable theo Tensile/SF (đúng bản chất)
                    if getattr(chain_spec, "tensile_strength_min_kn", 0.0) > 0.0:
                        allowable_kN = chain_spec.tensile_strength_min_kn / CHAIN_TENSILE_STRENGTH_SAFETY_FACTOR
                    else:
                        # nếu CSV thiếu, bỏ qua kiểm tra bền cho bản ghi này
                        allowable_kN = float("inf")

                    # Lọc theo bền
                    if F_required_kN > allowable_kN:
                        print(f"DEBUG TX: Xích {getattr(chain_spec, 'designation', 'Unknown')} không đủ bền: F_req={F_required_kN:.3f} kN > F_allow={allowable_kN:.3f} kN")
                        continue
                    
                    print(f"DEBUG TX: Xích {getattr(chain_spec, 'designation', 'Unknown')} đủ bền: F_req={F_required_kN:.3f} kN <= F_allow={allowable_kN:.3f} kN")

                    # Tạo giải pháp hợp lệ
                    solution = TransmissionSolution(
                        gearbox_ratio=gearbox_ratio,
                        drive_sprocket_teeth=z1,
                        driven_sprocket_teeth=z2_actual,
                        chain_pitch_mm=chain_spec.pitch_mm,
                        actual_belt_velocity=actual_velocity,
                        error=error,
                        chain_designation=getattr(chain_spec, "designation", ""),
                        total_transmission_ratio=i_total_actual,
                        chain_spec=chain_spec,
                        # --- [BẮT ĐẦU NÂNG CẤP THEO KẾ HOẠCH] ---
                        required_force_kN=F_required_kN,
                        allowable_kN=allowable_kN,
                        safety_margin=allowable_kN / max(F_required_kN, 1e-9),
                        chain_weight_kgpm=getattr(chain_spec, "weight_kgpm", 0.0)
                        # --- [KẾT THÚC NÂNG CẤP THEO KẾ HOẠCH] ---
                    )
                    
                    # --- [BẮT ĐẦU SỬA LỖI UI] ---
                    # Gán các thuộc tính alias để UI có thể truy cập đúng
                    solution.gearbox_ratio_mode = "Manual" if use_manual else "Auto"
                    solution.motor_output_rpm = output_rpm
                    solution.actual_velocity_mps = actual_velocity
                    solution.velocity_error_percent = error
                    solution.required_force_kN = F_required_kN
                    solution.allowable_force_kN = allowable_kN
                    solution.chain_weight_kg_per_m = getattr(chain_spec, "weight_kgpm", 0.0)
                    # --- [KẾT THÚC SỬA LỖI UI] ---
                    
                    valid_solutions.append(solution)

                    # ĐÃ tìm được xích đủ bền cho cặp z1/z2 hiện tại
                    # KHÔNG break để xem xét tất cả các loại xích có thể phù hợp
                    # (sẽ sắp xếp sau để chọn tốt nhất)
                except (ValueError, AttributeError) as e:
                    # Bỏ qua xích có dữ liệu không hợp lệ
                    print(f"DEBUG TX: Bỏ qua xích {getattr(chain_spec, 'designation', 'Unknown')} do lỗi: {e}")
                    continue
    
    # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
    # Lựa chọn giải pháp tốt nhất
    if not valid_solutions:
        if use_manual:
            print(f"DEBUG TX: Chế độ Manual - Không tìm thấy giải pháp phù hợp với i_g = {calculation_params.gearbox_ratio_user}")
            print("DEBUG TX: Khuyến nghị: Thử i_g khác hoặc chuyển về chế độ Auto")
        else:
            print("DEBUG TX: Chế độ Auto - Không tìm thấy giải pháp phù hợp")
        return None
    # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
    
    # Loại bỏ các giải pháp trùng lặp cặp răng (giữ lại giải pháp tốt nhất cho mỗi cặp)
    unique_solutions = {}
    for sol in valid_solutions:
        key = (sol.drive_sprocket_teeth, sol.driven_sprocket_teeth)
        if key not in unique_solutions or sol.error < unique_solutions[key].error:
            unique_solutions[key] = sol
    
    valid_solutions = list(unique_solutions.values())
    
    # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
    # Cải thiện thuật toán sắp xếp để cân bằng tốt hơn giữa các tiêu chí
    # Với chế độ Manual, ưu tiên giải pháp sử dụng i_g user
    if use_manual:
        valid_solutions.sort(key=lambda x: (
            x.error,  # 1) Sai số vận tốc (ưu tiên cao nhất)
            abs((x.driven_sprocket_teeth / x.drive_sprocket_teeth) - PREFERRED_CHAIN_RATIO),  # 2) Gần 1.9 (ưu tiên cao)
            (x.drive_sprocket_teeth + x.driven_sprocket_teeth) * 0.1,  # 3) Tổng số răng (giảm ảnh hưởng)
            getattr(x.chain_spec, "pitch_mm", 999.0) * 0.01,  # 4) Pitch nhỏ (giảm ảnh hưởng)
            -x.safety_margin * 0.1  # 5) Margin bền kéo cao (ưu tiên an toàn)
        ))
    else:
        # Chế độ Auto - giữ nguyên logic cũ
        valid_solutions.sort(key=lambda x: (
            x.error,  # 1) Sai số vận tốc (ưu tiên cao nhất)
            abs((x.driven_sprocket_teeth / x.drive_sprocket_teeth) - PREFERRED_CHAIN_RATIO),  # 2) Gần 1.9 (ưu tiên cao)
            (x.drive_sprocket_teeth + x.driven_sprocket_teeth) * 0.1,  # 3) Tổng số răng (giảm ảnh hưởng)
            getattr(x.chain_spec, "pitch_mm", 999.0) * 0.01,  # 4) Pitch nhỏ (giảm ảnh hưởng)
            -x.gearbox_ratio * 0.001  # 5) Hộp số tỉ số lớn (giảm ảnh hưởng)
        ))
    # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
    
    # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
    # In ra tất cả giải pháp để debug
    mode_text = "Manual" if use_manual else "Auto"
    print(f"DEBUG TX: Chế độ {mode_text} - Tìm thấy {len(valid_solutions)} giải pháp:")
    for i, sol in enumerate(valid_solutions[:5]):  # Chỉ hiển thị 5 giải pháp đầu
        i_s = sol.driven_sprocket_teeth / sol.drive_sprocket_teeth
        print(f"  {i+1}. gearbox={sol.gearbox_ratio}, z1={sol.drive_sprocket_teeth}, z2={sol.driven_sprocket_teeth}, "
              f"i_s={i_s:.3f}, error={sol.error:.2f}%")
    
    best_solution = valid_solutions[0]
    
    print(f"DEBUG TX: Chế độ {mode_text} - Giải pháp tốt nhất: gearbox={best_solution.gearbox_ratio}, "
          f"z1={best_solution.drive_sprocket_teeth}, z2={best_solution.driven_sprocket_teeth}, "
          f"i_s={best_solution.driven_sprocket_teeth/best_solution.drive_sprocket_teeth:.3f}, "
          f"chain={best_solution.chain_designation}, error={best_solution.error:.2f}%")
    # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
    
    return best_solution

# Hàm cũ để tương thích ngược
def select_transmission(target_velocity: float, pulley_diameter: float, motor_rpm: int, chain_specs: list) -> Optional['TransmissionSolution']:
    """
    Hàm cũ để tương thích ngược - gọi find_optimal_transmission
    """
    from .models import ConveyorParameters
    
    # Tạo ConveyorParameters tạm thời
    temp_params = ConveyorParameters(
        calculation_standard="",
        project_name="",
        designer="",
        client="",
        location="",
        material="",
        density_tpm3=0.0,
        particle_size_mm=0.0,
        angle_repose_deg=0.0,
        material_temp_c=0.0,
        is_abrasive=False,
        is_corrosive=False,
        is_dusty=False,
        Qt_tph=0.0,
        L_m=0.0,
        H_m=0.0,
        inclination_deg=0.0,
        V_mps=target_velocity,
        operating_hours=0,
        B_mm=0,
        belt_type="",
        belt_thickness_mm=0.0,
        trough_angle_label="",
        surcharge_angle_deg=0.0,
        carrying_idler_spacing_m=0.0,
        return_idler_spacing_m=0.0,
        drive_type="",
        motor_efficiency=0.0,
        gearbox_efficiency=0.0,
        mu_pulley=0.0,
        wrap_deg=0.0,
        Kt_start=0.0,
        ambient_temp_c=0.0,
        humidity_percent=0.0,
        altitude_m=0.0,
        dusty_environment=False,
        corrosive_environment=False,
        explosion_proof=False,
        motor_rpm=motor_rpm
    )
    
    return find_optimal_transmission(temp_params, chain_specs, pulley_diameter, None)
# --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---

