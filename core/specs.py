# -*- coding: utf-8 -*-
from typing import List
try:
    from .models import MaterialType, BeltType
except ImportError:
    # Fallback cho trường hợp chạy trực tiếp
    from models import MaterialType, BeltType
G = 9.81
VERSION = "3.5 Professional (Enhanced Chain Support)"
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

# --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
# Danh sách tỉ số truyền tiêu chuẩn của hộp số giảm tốc
# Sắp xếp theo thứ tự giảm dần để ưu tiên chi phí (tỷ số cao thường ít cấp hơn, rẻ hơn)
STANDARD_GEARBOX_RATIOS = [100, 80, 60, 50, 40, 30, 25, 20, 15, 12.5, 10, 8, 6, 5]

# --- [BẮT ĐẦU NÂNG CẤP THEO KẾ HOẠCH] ---
# Hằng số an toàn & sở thích
CHAIN_SAFETY_FACTOR = 8.0
PREFERRED_CHAIN_RATIO = 1.9
PREFERRED_CHAIN_RANGE = (1.6, 2.2)
CHAIN_WEIGHT_IMPORTANCE = 0.1
# --- [KẾT THÚC NÂNG CẤP THEO KẾ HOẠCH] ---

# Hằng số an toàn cho xích (dùng trong kiểm tra độ bền) - ĐIỀU CHỈNH XUỐNG MỨC HỢP LÝ
CHAIN_TENSILE_STRENGTH_SAFETY_FACTOR = 4

# Tỉ số truyền nhông-xích ưu tiên (để giảm mài mòn) - GIỮ LẠI ĐỂ TƯƠNG THÍCH
PREFERRED_CHAIN_RATIO = 1.9
PREFERRED_CHAIN_RANGE = (1.6, 2.2)

def load_chain_data() -> List['ChainSpec']:
    """
    Tải dữ liệu xích từ file Bang tra 1.csv
    Trả về danh sách các ChainSpec với dữ liệu thực từ CSV
    """
    from .models import ChainSpec
    import csv
    import os
    
    chain_specs = []
    
    # Đường dẫn đến file CSV (sử dụng dữ liệu đã cập nhật có Measuring Load & Tensile Strength thực)
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Bang tra 1.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Kiểm tra có ít nhất một trong hai mã xích (ANSI hoặc ISO)
                ansi_code = (row.get('ANSI Standard Chain Code') or '').strip()
                iso_code = (row.get('ISO Standard Chain Code') or '').strip()
                
                # Bỏ qua các hàng trống hoặc không có mã xích nào
                if not ansi_code and not iso_code:
                    continue
                
                # Xử lý dữ liệu từ file CSV (dùng dữ liệu thực, không ước lượng)
                try:
                    pitch_mm = float(row['Pitch P (mm)'].replace(',', '.'))
                    weight_kgpm = float(row['Weight kg/m'].replace(',', '.'))
                    iso_code = (row.get('ISO Standard Chain Code') or '').strip()
                    ansi_code = (row.get('ANSI Standard Chain Code') or '').strip()
                    strand_txt = (row.get('Strand') or '1R').strip().upper()
                    strand = int(strand_txt.replace('R', '') or 1)

                    # --- [BẮT ĐẦU NÂNG CẤP THEO KẾ HOẠCH] ---
                    # Tensile Strength (min kN) - dùng để tính allowable (lực kéo cho phép)
                    tensile_strength_min_kn = float(row['Tensile Strength (min kN)'].replace(',', '.'))
                    # Measuring Load (min N) - chỉ dùng tham khảo, KHÔNG dùng làm allowable
                    measuring_load_min_n = float(row['Measuring Load (min N)'].replace(',', '.'))
                    measuring_load_min_kn = measuring_load_min_n / 1000.0
                    # --- [KẾT THÚC NÂNG CẤP THEO KẾ HOẠCH] ---

                    # Tạo designation kết hợp cả ANSI và ISO nếu có
                    if ansi_code and iso_code:
                        designation = f"{ansi_code}/{iso_code} (ANSI/ISO)"
                    elif ansi_code:
                        designation = f"{ansi_code} (ANSI)"
                    else:
                        designation = f"{iso_code} (ISO)"

                    chain_spec = ChainSpec(
                        designation=designation,
                        iso_code=iso_code,
                        ansi_code=ansi_code,
                        strand=strand,
                        pitch_mm=pitch_mm,
                        inner_width_mm=float(row['Inner Width W (mm)'].replace(',', '.')),
                        roller_diameter_mm=float(row['Roller Diameter D (mm)'].replace(',', '.')),
                        pin_diameter_mm=float(row['Pin Diameter d (mm)'].replace(',', '.')),
                        plate_thickness_mm=float(row['Plate Thickness T (mm)'].replace(',', '.')),
                        weight_kgpm=weight_kgpm,
                        # giữ trường bền cũ (nếu nơi khác dùng), nhưng ưu tiên trường mới bên dưới
                        tensile_strength_single_kn=0.0,
                        tensile_strength_double_kn=0.0,
                        tensile_strength_triple_kn=0.0,
                        # --- [BẮT ĐẦU NÂNG CẤP THEO KẾ HOẠCH] ---
                        # Trường mới từ CSV - Tensile Strength dùng để tính allowable
                        tensile_strength_min_kn=tensile_strength_min_kn,
                        # Measuring Load chỉ dùng tham khảo, KHÔNG dùng làm allowable
                        measuring_load_min_kn=measuring_load_min_kn
                        # --- [KẾT THÚC NÂNG CẤP THEO KẾ HOẠCH] ---
                    )
                    chain_specs.append(chain_spec)
                except (ValueError, KeyError):
                    # Bỏ qua các hàng có dữ liệu không hợp lệ
                    continue

    except FileNotFoundError:
        print(f"Không tìm thấy file CSV: {csv_path}")
    except Exception as e:
        print(f"Lỗi khi đọc file CSV: {e}")
    
    return chain_specs

# Danh sách xích đã tải (cache)
ACTIVE_CHAIN_SPECS = load_chain_data()

# --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---
