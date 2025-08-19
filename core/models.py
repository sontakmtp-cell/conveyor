# title="core/models.py" contentType="text/python"
# core/models.py
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

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

