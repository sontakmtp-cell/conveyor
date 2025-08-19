# -*- coding: utf-8 -*-
from .models import MaterialType, BeltType
G = 9.81
VERSION = "2.1 Professional (Refactored)"
COPYRIGHT = "Mọi thắc mắc và góp ý xin gửi về haingocson@gmail.com"

STANDARD_WIDTHS = [300, 400, 450, 500, 600, 650, 750, 800, 900, 1000, 1050, 1200, 1400, 1600, 1800, 2000, 2200]

# DB mặc định - ĐÃ CẬP NHẬT THEO FILE PDF
# Tham khảo: Bảng 6, trang 9, "Hướng dẫn tính toán băng tải"
MATERIAL_DB = {
    # Tên vật liệu: {"density": (tấn/m³), ...các thông số khác...}
    # Với các khoảng giá trị trong PDF, giá trị trung bình đã được lấy.
    MaterialType.SAND_DRY.value: {"density": 1.56, "angle_repose": 20, "v_max": 3.0, "abrasive": "high", "temperature_max": 60, "moisture": "very_low", "corrosive": False},
    MaterialType.SAND_WET.value: {"density": 1.92, "angle_repose": 30, "v_max": 2.5, "abrasive": "high", "temperature_max": 60, "moisture": "high", "corrosive": False},
    MaterialType.SOFT_ROCK.value: {"density": 1.68, "angle_repose": 35, "v_max": 3.0, "abrasive": "medium", "temperature_max": 90, "moisture": "low", "corrosive": False},
    MaterialType.BROKEN_TRAP_ROCK.value: {"density": 1.72, "angle_repose": 35, "v_max": 2.5, "abrasive": "high", "temperature_max": 90, "moisture": "low", "corrosive": False},
    MaterialType.LIMESTONE.value: {"density": 1.56, "angle_repose": 30, "v_max": 3.0, "abrasive": "medium", "temperature_max": 90, "moisture": "low", "corrosive": False},
    MaterialType.DRY_SOIL.value: {"density": 1.2, "angle_repose": 30, "v_max": 3.5, "abrasive": "low", "temperature_max": 60, "moisture": "low", "corrosive": False},
    MaterialType.DRY_CLAY.value: {"density": 1.1, "angle_repose": 30, "v_max": 3.5, "abrasive": "medium", "temperature_max": 80, "moisture": "low", "corrosive": False},
    MaterialType.WET_CLAY.value: {"density": 1.6, "angle_repose": 35, "v_max": 3.0, "abrasive": "medium", "temperature_max": 80, "moisture": "high", "corrosive": False},
    MaterialType.WET_SOIL.value: {"density": 1.72, "angle_repose": 35, "v_max": 3.0, "abrasive": "low", "temperature_max": 60, "moisture": "high", "corrosive": False},
    MaterialType.WOOD.value: {"density": 0.68, "angle_repose": 40, "v_max": 3.5, "abrasive": "low", "temperature_max": 60, "moisture": "high", "corrosive": False},
    MaterialType.BARLEY.value: {"density": 0.61, "angle_repose": 25, "v_max": 4.0, "abrasive": "low", "temperature_max": 50, "moisture": "medium", "corrosive": False},
    MaterialType.ROCK_SALT.value: {"density": 0.77, "angle_repose": 30, "v_max": 3.5, "abrasive": "low", "temperature_max": 70, "moisture": "low", "corrosive": True},
    MaterialType.CRUSHED_SALT.value: {"density": 1.2, "angle_repose": 30, "v_max": 3.5, "abrasive": "medium", "temperature_max": 70, "moisture": "low", "corrosive": True},
    MaterialType.ALUMINUM_GRANULES.value: {"density": 0.88, "angle_repose": 25, "v_max": 4.0, "abrasive": "medium", "temperature_max": 80, "moisture": "low", "corrosive": False},
    MaterialType.ALUMINUM_POWDER.value: {"density": 0.76, "angle_repose": 25, "v_max": 5.0, "abrasive": "low", "temperature_max": 80, "moisture": "very_low", "corrosive": False},
    MaterialType.COPPER_ORE.value: {"density": 2.24, "angle_repose": 40, "v_max": 3.0, "abrasive": "very_high", "temperature_max": 100, "moisture": "low", "corrosive": False},
    MaterialType.BAUXITE.value: {"density": 0.9, "angle_repose": 35, "v_max": 3.5, "abrasive": "high", "temperature_max": 100, "moisture": "variable", "corrosive": False},
    MaterialType.IRON_ORE.value: {"density": 2.48, "angle_repose": 40, "v_max": 3.0, "abrasive": "very_high", "temperature_max": 100, "moisture": "low", "corrosive": False},
    MaterialType.COKE_POWDER.value: {"density": 0.47, "angle_repose": 35, "v_max": 4.0, "abrasive": "high", "temperature_max": 120, "moisture": "low", "corrosive": False},
    MaterialType.REFINED_COKE.value: {"density": 0.6, "angle_repose": 35, "v_max": 4.0, "abrasive": "medium", "temperature_max": 120, "moisture": "low", "corrosive": False},
    MaterialType.COAL.value: {"density": 0.9, "angle_repose": 35, "v_max": 5.0, "abrasive": "medium", "temperature_max": 80, "moisture": "low", "corrosive": False},
    MaterialType.COAL_MINING.value: {"density": 0.68, "angle_repose": 35, "v_max": 4.5, "abrasive": "medium", "temperature_max": 80, "moisture": "variable", "corrosive": False},
    MaterialType.CEMENT_CLINKER.value: {"density": 1.4, "angle_repose": 30, "v_max": 4.0, "abrasive": "high", "temperature_max": 120, "moisture": "very_low", "corrosive": True},
    MaterialType.PORTLAND_CEMENT.value: {"density": 1.5, "angle_repose": 25, "v_max": 6.0, "abrasive": "medium", "temperature_max": 120, "moisture": "very_low", "corrosive": True},
}

BELT_SPECS = {
    # Thêm 'cost_per_m2' (chi phí USD cho mỗi mét vuông băng)
    BeltType.FABRIC_EP.value: {"strength": 1000, "elongation": 1.5, "temp_max": 120, "layers": [2,3,4,5,6], "T_allow_Npm": 10_000, "cost_per_m2": 45.0},
    BeltType.FABRIC_NN.value: {"strength": 800, "elongation": 2.0, "temp_max": 100, "layers": [2,3,4,5], "T_allow_Npm": 8_000, "cost_per_m2": 40.0},
    BeltType.STEEL_CORD.value: {"strength": 2500, "elongation": 0.2, "temp_max": 150, "layers": [1], "T_allow_Npm": 20_000, "cost_per_m2": 120.0},
    BeltType.PVC.value: {"strength": 400, "elongation": 3.0, "temp_max": 80, "layers": [1,2], "T_allow_Npm": 4_000, "cost_per_m2": 35.0},
    BeltType.RUBBER.value: {"strength": 630, "elongation": 1.8, "temp_max": 100, "layers": [2,3,4], "T_allow_Npm": 6_300, "cost_per_m2": 55.0},
}

# Trạng thái DB đang dùng (có thể thay trong runtime)
ACTIVE_MATERIAL_DB = MATERIAL_DB.copy()
ACTIVE_BELT_SPECS = BELT_SPECS.copy()
