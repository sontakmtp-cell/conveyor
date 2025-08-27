# -*- coding: utf-8 -*-
import math
from .specs import STANDARD_WIDTHS, ACTIVE_MATERIAL_DB

def optimize_belt_width(capacity_tph: float, density_tpm3: float, speed_mps: float) -> int:
    mass_flow = capacity_tph*1000/3600
    volume_flow = mass_flow/(density_tpm3*1000)
    required_area = volume_flow/max(speed_mps, 0.1)
    required_area *= 1.2
    est_width = math.sqrt(required_area/0.1)*1000
    return min(STANDARD_WIDTHS, key=lambda w: abs(w-est_width))

def optimize_speed(material_name: str, particle_mm: float, belt_width_mm: int) -> float:
    """Tối ưu hóa tốc độ băng dựa trên vật liệu và kích thước hạt."""
    try:
        data = ACTIVE_MATERIAL_DB.get(material_name, {})
        vmax = data.get("v_max", 4.0)
        
        # Tính tốc độ khuyến nghị dựa trên kích thước hạt
        if particle_mm > 200:
            rec = vmax * 0.6
        elif particle_mm > 50:
            rec = vmax * 0.8
        else:
            rec = vmax * 0.9
        
        # Điều chỉnh theo bề rộng băng
        if belt_width_mm >= 1200:
            rec = min(rec * 1.1, vmax)
        
        return round(rec, 2)
        
    except Exception as e:
        print(f"Warning: Error in optimize_speed for {material_name}: {e}")
        # Fallback: tốc độ an toàn mặc định
        return 2.0

def get_max_speed_from_table(belt_width_mm: int, material_characteristics: dict) -> float:
    """
    Lấy tốc độ tối đa cho phép từ bảng tra dựa trên bề rộng băng và đặc tính vật liệu.
    
    Args:
        belt_width_mm: Bề rộng băng (mm)
        material_characteristics: Dict chứa các đặc tính vật liệu được chọn
        
    Returns:
        float: Tốc độ tối đa cho phép (m/s)
    """
    try:
        import pandas as pd
        import os
        
        # Đường dẫn đến file CSV
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'hidden', 'Bang tra toc do bang tai.csv')
        
        if not os.path.exists(csv_path):
            print(f"Warning: Không tìm thấy file bảng tra tốc độ: {csv_path}")
            return 5.0  # Giá trị mặc định an toàn
        
        # Đọc file CSV
        df = pd.read_csv(csv_path)
        
        # Tìm bề rộng băng gần nhất
        available_widths = df['conveyor width (mm)'].dropna().tolist()
        if not available_widths:
            return 5.0
        
        # Tìm bề rộng gần nhất (có thể nhỏ hơn hoặc bằng)
        belt_width_mm = int(belt_width_mm)
        # Lọc ra các bề rộng hợp lệ (chỉ số)
        valid_widths = []
        for width in available_widths:
            try:
                valid_widths.append(int(width))
            except (ValueError, TypeError):
                continue
        
        if not valid_widths:
            return 5.0  # Giá trị mặc định an toàn
        
        closest_width = min(valid_widths, key=lambda x: abs(x - belt_width_mm))
        
        # Xác định cột tốc độ dựa trên đặc tính vật liệu
        if material_characteristics.get('is_abrasive', False):
            # Vật liệu hạt (ngũ cốc, than...) - checkbox "Granular materials"
            speed_column = 'Granular materials (m/s)'
        elif material_characteristics.get('is_corrosive', False):
            # Vật liệu mài mòn (cát, xi măng, bột...) - checkbox "Coal and abrasive materials"
            speed_column = 'Coal and abrasive materials (m/s)'
        elif material_characteristics.get('is_dusty', False):
            # Vật liệu cứng, có cạnh sắc (quặng, đá, kim loại...) - checkbox "Hard ores, rocks and materials with sharp edges"
            speed_column = 'Hard ores, rocks and materials with sharp edges (m/s)'
        else:
            # Mặc định: vật liệu hạt (ngũ cốc, than...)
            speed_column = 'Granular materials (m/s)'
        
        # Lấy tốc độ tối đa
        row = df[df['conveyor width (mm)'] == closest_width]
        if not row.empty:
            max_speed = row[speed_column].iloc[0]
            if pd.isna(max_speed):
                # Nếu không có giá trị, sử dụng cột khác theo thứ tự ưu tiên:
                # 1. Granular materials (vật liệu hạt - an toàn nhất)
                # 2. Coal and abrasive materials (vật liệu mài mòn)
                # 3. Hard ores, rocks and materials with sharp edges (vật liệu cứng - nguy hiểm nhất)
                for col in ['Granular materials (m/s)', 'Coal and abrasive materials (m/s)', 'Hard ores, rocks and materials with sharp edges (m/s)']:
                    if not pd.isna(row[col].iloc[0]):
                        max_speed = row[col].iloc[0]
                        break
                else:
                    max_speed = 5.0  # Giá trị mặc định an toàn
            return float(max_speed)
        
        return 5.0  # Giá trị mặc định
        
    except Exception as e:
        print(f"Warning: Lỗi khi đọc bảng tra tốc độ: {e}")
        return 5.0  # Giá trị mặc định an toàn

def calculate_belt_speed(capacity_tph: float, density_tpm3: float, belt_width_mm: int, 
                         particle_mm: float, material_name: str, trough_angle_deg: float = 20.0, 
                         surcharge_angle_deg: float = 20.0, material_characteristics: dict = None) -> tuple:
    """
    Tính toán tốc độ băng cần thiết và khuyến nghị.
    
    Args:
        capacity_tph: Lưu lượng yêu cầu (tấn/h)
        density_tpm3: Khối lượng riêng (tấn/m³)
        belt_width_mm: Bề rộng băng (mm)
        particle_mm: Kích thước hạt (mm)
        material_name: Tên vật liệu
        trough_angle_deg: Góc máng (độ)
        surcharge_angle_deg: Góc surcharge (độ)
        material_characteristics: Dict chứa đặc tính vật liệu được chọn
    
    Returns:
        tuple: (v_final, v_req, v_rec, area_m2, warnings, max_speed_allowed)
    """
    
    # 1) Tính lưu lượng khối lượng (kg/s)
    mass_flow_kgps = capacity_tph * 1000.0 / 3600.0
    
    # 2) Chuyển đổi khối lượng riêng (kg/m³)
    density_kgm3 = density_tpm3 * 1000.0
    
    # 3) Tính tiết diện (m²) - sử dụng logic từ trough_utils
    import math
    belt_width_m = float(belt_width_mm) / 1000.0
    trough_angle_rad = math.radians(float(trough_angle_deg))
    surcharge_angle_rad = math.radians(float(surcharge_angle_deg))
    
    # Cross-sectional area: bottom wedge + side rise with trough
    A_bottom = 0.25 * belt_width_m * belt_width_m * math.tan(surcharge_angle_rad)
    A_sides = (belt_width_m * belt_width_m / 8.0) * (1.0 - math.cos(trough_angle_rad))
    area_m2 = max(0.0, A_bottom + A_sides)
    
    # 4) Tính tốc độ cần thiết (m/s)
    v_req = mass_flow_kgps / (density_kgm3 * area_m2)
    
    # 5) Lấy tốc độ khuyến nghị
    v_rec = optimize_speed(material_name, particle_mm, belt_width_mm)
    
    # 6) Lấy tốc độ tối đa cho phép từ bảng tra
    if material_characteristics is None:
        material_characteristics = {}
    max_speed_allowed = get_max_speed_from_table(belt_width_mm, material_characteristics)
    
    # 7) So sánh và đưa ra cảnh báo
    warnings = []
    from .specs import BELT_SPEED_SAFETY_MARGIN
    
    # Cảnh báo về tốc độ vượt quá khuyến nghị
    if v_req > v_rec * (1 + BELT_SPEED_SAFETY_MARGIN):
        warnings.append(
            f"Tốc độ cần thiết ({v_req:.2f} m/s) vượt quá tốc độ khuyến nghị "
            f"({v_rec:.2f} m/s) + {BELT_SPEED_SAFETY_MARGIN*100:.0f}% margin. "
            f"Cân nhắc tăng bề rộng băng hoặc giảm lưu lượng."
        )
    
    # Cảnh báo về tốc độ vượt quá tối đa cho phép
    if v_req > max_speed_allowed:
        warnings.append(
            f"⚠️ CẢNH BÁO: Tốc độ tính toán ({v_req:.2f} m/s) vượt quá tốc độ tối đa cho phép "
            f"({max_speed_allowed:.2f} m/s) theo bảng tra cho bề rộng {belt_width_mm}mm. "
            f"Thiết kế này KHÔNG TỐI ƯU - cần tăng bề rộng băng hoặc giảm lưu lượng."
        )
    
    # 8) Tốc độ cuối cùng (có thể điều chỉnh theo logic nghiệp vụ)
    v_final = v_req
    
    return v_final, v_req, v_rec, area_m2, warnings, max_speed_allowed

def optimize_belt_width_for_capacity(capacity_tph: float, density_tpm3: float, 
                                   particle_mm: float, material_name: str, 
                                   trough_angle_deg: float = 20.0, 
                                   surcharge_angle_deg: float = 20.0) -> tuple:
    """
    Tối ưu hóa bề rộng băng dựa trên lưu lượng, không cần tốc độ đầu vào.
    
    Args:
        capacity_tph: Lưu lượng yêu cầu (tấn/h)
        density_tpm3: Khối lượng riêng (tấn/m³)
        particle_mm: Kích thước hạt (mm)
        material_name: Tên vật liệu
        trough_angle_deg: Góc máng (độ)
        surcharge_angle_deg: Góc surcharge (độ)
    
    Returns:
        tuple: (belt_width_mm, v_final, v_req, v_rec, area_m2, warnings)
    """
    from .specs import BELT_SPEED_SAFETY_MARGIN
    warnings = []
    
    # Duyệt qua các bề rộng tiêu chuẩn từ nhỏ đến lớn (đã sort để đảm bảo thứ tự)
    for width_mm in sorted(STANDARD_WIDTHS):
        try:
            v_final, v_req, v_rec, area_m2, width_warnings, max_speed_allowed = calculate_belt_speed(
                capacity_tph, density_tpm3, width_mm, particle_mm, material_name,
                trough_angle_deg, surcharge_angle_deg
            )
            
            # Nếu tốc độ cần thiết <= tốc độ khuyến nghị + margin -> chọn bề rộng này
            if v_req <= v_rec * (1 + BELT_SPEED_SAFETY_MARGIN):
                warnings.extend(width_warnings)
                return width_mm, v_final, v_req, v_rec, area_m2, warnings
            
        except Exception as e:
            warnings.append(f"Lỗi khi tính toán với bề rộng {width_mm}mm: {str(e)}")
            continue
    
    # Nếu không tìm được bề rộng phù hợp, chọn bề rộng lớn nhất
    max_width = max(STANDARD_WIDTHS)
    warnings.append(
        f"Không tìm được bề rộng phù hợp. Sử dụng bề rộng lớn nhất ({max_width}mm) "
        f"và phát cảnh báo về tốc độ."
    )
    
    # Tính toán với bề rộng lớn nhất
    try:
        v_final, v_req, v_rec, area_m2, width_warnings, max_speed_allowed = calculate_belt_speed(
            capacity_tph, density_tpm3, max_width, particle_mm, material_name,
            trough_angle_deg, surcharge_angle_deg
        )
        warnings.extend(width_warnings)
        return max_width, v_final, v_req, v_rec, area_m2, warnings
    except Exception as e:
        # Fallback cuối cùng
        warnings.append(f"Lỗi khi tính toán với bề rộng lớn nhất: {str(e)}")
        return max_width, 2.0, 2.0, 2.0, 0.0, warnings
