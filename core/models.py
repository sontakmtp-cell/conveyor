# title="core/models.py" contentType="text/python"
# core/models.py
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional

class MaterialType(Enum):
    COAL = "Than đá"
    GRAVEL = "Sỏi"
    GRAIN = "Ngũ cốc"
    WOOD_CHIPS = "Dăm gỗ"
    SAND_DRY = "Cát khô"
    SAND_WET = "Cát ướt"
    SOFT_ROCK = "Đá mềm"
    BROKEN_TRAP_ROCK = "Đá tráp, vỡ"
    LIMESTONE = "Đá vôi"
    DRY_SOIL = "Đất khô"
    DRY_CLAY = "Đất sét khô"
    WET_CLAY = "Đất sét ướt"
    WET_SOIL = "Đất ướt"
    WOOD = "Gỗ"
    BARLEY = "Lúa mạch"
    ROCK_SALT = "Muối mỏ"
    CRUSHED_SALT = "Muối nghiền"
    ALUMINUM_GRANULES = "Nhôm hạt"
    ALUMINUM_POWDER = "Nhôm tán mịn"
    COPPER_ORE = "Quặng đồng"
    BAUXITE = "Quặng nhôm (Bauxite)"
    IRON_ORE = "Quặng sắt"
    COKE_POWDER = "Than cốc dạng cám"
    REFINED_COKE = "Than cốc tinh"
    COAL_MINING = "Than mỏ"
    CEMENT_CLINKER = "Xi măng Clinker"
    PORTLAND_CEMENT = "Xi măng Portland (khô)"

class BeltType(Enum):
    FABRIC_EP = "Vải EP (Polyester)"
    FABRIC_NN = "Vải NN (Nylon)"
    STEEL_CORD = "Dây thép (ST)"
    PVC = "PVC"
    RUBBER = "Cao su"

@dataclass
class ConveyorParameters:
    calculation_standard: str
    project_name: str
    designer: str
    client: str
    location: str
    material: str
    density_tpm3: float
    particle_size_mm: float
    angle_repose_deg: float
    material_temp_c: float
    is_abrasive: bool
    is_corrosive: bool
    is_dusty: bool
    Qt_tph: float
    L_m: float
    H_m: float
    inclination_deg: float
    V_mps: float
    operating_hours: int
    B_mm: int
    belt_type: str
    belt_thickness_mm: float
    trough_angle_label: str
    surcharge_angle_deg: float
    carrying_idler_spacing_m: float
    return_idler_spacing_m: float
    drive_type: str
    motor_efficiency: float
    gearbox_efficiency: float
    mu_pulley: float
    wrap_deg: float
    Kt_start: float
    ambient_temp_c: float
    humidity_percent: float
    altitude_m: float
    dusty_environment: bool
    corrosive_environment: bool
    explosion_proof: bool
    # --- [BẮT ĐẦU NÂNG CẤP] ---
    # Thêm trường để nhận tùy chọn phân phối lực từ UI cho truyền động kép
    dual_drive_ratio: str = "Phân phối lý thuyết"
    # --- [KẾT THÚC NÂNG CẤP] ---
    
    # --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
    # Tốc độ động cơ (vòng/phút)
    motor_rpm: int = 1450
    # --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---
    
    db_path: str = ""

@dataclass
class CalculationResult:
    mass_flow_rate: float = 0.0
    Qt_effective_tph: float = 0.0
    Qt_calc_tph: float = 0.0
    cross_section_area_m2: float = 0.0

    material_load_kgpm: float = 0.0
    belt_weight_kgpm: float = 0.0
    moving_parts_weight_kgpm: float = 0.0
    total_load_kgpm: float = 0.0

    lift_force: float = 0.0
    friction_force: float = 0.0
    effective_tension: float = 0.0
    T1: float = 0.0
    T2: float = 0.0
    max_tension: float = 0.0

    P1_kw: float = 0.0
    P2_kw: float = 0.0
    P3_kw: float = 0.0
    Pt_kw: float = 0.0
    required_power_kw: float = 0.0
    motor_power_kw: float = 0.0

    efficiency: float = 0.0
    drive_efficiency_percent: float = 0.0

    safety_factor: float = 0.0
    belt_strength_utilization: float = 0.0
    capacity_utilization: float = 0.0

    drum_diameter_mm: float = 0.0
    wrap_angle_rad: float = 0.0

    cost_capital_total: float = 0.0
    cost_belt: float = 0.0
    cost_idlers: float = 0.0
    cost_structure: float = 0.0
    cost_drive: float = 0.0
    cost_others: float = 0.0
    op_cost_energy_per_year: float = 0.0
    op_cost_maintenance_per_year: float = 0.0
    op_cost_total_per_year: float = 0.0

    distances_m: List[float] = field(default_factory=list)
    tension_profile: List[float] = field(default_factory=list)
    lift_force_profile: List[float] = field(default_factory=list)
    friction_force_profile: List[float] = field(default_factory=list)
    t2_profile: List[float] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    recommended_pulley_diameters_mm: Dict[str, float] = field(default_factory=dict)
    recommended_idler_spacing_m: Dict[str, float] = field(default_factory=dict)
    transition_distance_m: float = 0.0

    # --- [BẮT ĐẦU NÂNG CẤP] ---
    # Các trường mới cho kết quả tính toán truyền động kép (Mục 6.2, PDF)
    drive_distribution_method: str = ""  # Lưu phương pháp phân phối (Lý thuyết, 50/50, etc.)
    Fp1: float = 0.0                     # Lực vòng tại Puly 1 (chính) [kg]
    Fp2: float = 0.0                     # Lực vòng tại Puly 2 (phụ) [kg]
    F11: float = 0.0                     # Lực căng nhánh căng tại Puly 1 (T_max của hệ thống) [N]
    F12: float = 0.0                     # Lực căng nhánh căng tại Puly 2 [N]
    F21: float = 0.0                     # Lực căng nhánh chùng tại Puly 1 [N]
    F22: float = 0.0                     # Lực căng nhánh chùng tại Puly 2 [N]
    Fc_drive: float = 0.0                # Lực thắng ma sát nhánh căng (công thức 19) [kg]
    Fr_drive: float = 0.0                # Lực thắng ma sát nhánh chùng (công thức 20) [kg]
    # --- [KẾT THÚC NÂNG CẤP] ---

    # --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
    # Kết quả tính toán bộ truyền động hoàn chỉnh
    transmission_solution: Optional['TransmissionSolution'] = None
    # --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---

# --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
# Model cho thông số xích
@dataclass
class ChainSpec:
    designation: str = ""  # Mã xích (ví dụ: 05B, 08A, 16B)
    pitch_mm: float = 0.0  # Bước xích (mm)
    inner_width_mm: float = 0.0  # Chiều rộng trong (mm)
    roller_diameter_mm: float = 0.0  # Đường kính con lăn (mm)
    pin_diameter_mm: float = 0.0  # Đường kính chốt (mm)
    plate_thickness_mm: float = 0.0  # Độ dày tấm (mm)
    weight_kgpm: float = 0.0  # Trọng lượng (kg/m)
    tensile_strength_single_kn: float = 0.0  # Độ bền kéo đơn dây (kN)
    tensile_strength_double_kn: float = 0.0  # Độ bền kéo đôi dây (kN)
    tensile_strength_triple_kn: float = 0.0  # Độ bền kéo ba dây (kN)

# Model cho giải pháp truyền động hoàn chỉnh
@dataclass
class TransmissionSolution:
    gearbox_ratio: float = 0.0  # Tỉ số truyền của hộp số
    drive_sprocket_teeth: int = 0  # Số răng nhông dẫn
    driven_sprocket_teeth: int = 0  # Số răng nhông bị dẫn
    chain_pitch_mm: float = 0.0  # Bước xích (mm)
    actual_belt_velocity: float = 0.0  # Vận tốc băng tải thực tế (m/s)
    error: float = 0.0  # Sai số so với vận tốc yêu cầu (%)
    chain_designation: str = ""  # Mã xích được chọn
    total_transmission_ratio: float = 0.0  # Tổng tỉ số truyền thực tế
    chain_spec: Optional[ChainSpec] = None  # Thông tin chi tiết về xích được chọn
# --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---

