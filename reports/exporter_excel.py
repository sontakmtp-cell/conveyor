# reports/exporter_excel.py
# -*- coding: utf-8 -*-
"""
Module xuất báo cáo Excel chuyên nghiệp, được thiết kế lại hoàn toàn.
Báo cáo bao gồm trang tổng quan (dashboard) với biểu đồ, các sheet dữ liệu chi tiết,
định dạng chuyên nghiệp và phân tích trực quan.
"""
import pandas as pd
from datetime import datetime
from core.models import CalculationResult, ConveyorParameters

def export_excel_report(path: str, params: ConveyorParameters, result: CalculationResult):
    """
    Xuất báo cáo chi tiết ra file Excel với nhiều sheet được định dạng chuyên nghiệp.
    """
    if not result:
        raise ValueError("Đối tượng kết quả (result) không được để trống.")

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        workbook = writer.book

        # --- Định nghĩa các định dạng cell ---
        formats = {
            'title': workbook.add_format({'bold': True, 'font_size': 18, 'font_color': '#2980B9', 'align': 'center', 'valign': 'vcenter'}),
            'subtitle': workbook.add_format({'bold': True, 'font_size': 12, 'font_color': '#34495E', 'align': 'left'}),
            'header': workbook.add_format({'bold': True, 'bg_color': '#34495E', 'font_color': 'white', 'border': 1, 'align': 'center'}),
            'group_header': workbook.add_format({'bold': True, 'bg_color': '#ECF0F1', 'font_color': '#2980B9', 'border': 1, 'font_size': 11}),
            'label': workbook.add_format({'bold': True, 'bg_color': '#F2F2F2', 'border': 1}),
            'value': workbook.add_format({'border': 1}),
            'money': workbook.add_format({'border': 1, 'num_format': '$ #,##0'}),
            'number': workbook.add_format({'border': 1, 'num_format': '#,##0.00'}),
            'percent': workbook.add_format({'border': 1, 'num_format': '0.0"%"'}),
            'status_ok': workbook.add_format({'bg_color': '#D5F5E3', 'font_color': '#186A3B', 'bold': True, 'border': 1}),
            'status_warn': workbook.add_format({'bg_color': '#FCF3CF', 'font_color': '#F39C12', 'bold': True, 'border': 1}),
            'status_danger': workbook.add_format({'bg_color': '#FADBD8', 'font_color': '#C0392B', 'bold': True, 'border': 1}),
        }

        # --- Ghi dữ liệu vào các sheet ---
        _write_summary_sheet(writer, params, result, formats)
        _write_inputs_sheet(writer, params, formats)
        _write_results_sheet(writer, result, formats)
        _write_structural_sheet(writer, result, formats)
        _write_cost_sheet(writer, result, formats)
        _write_data_profile_sheet(writer, result, formats) # Sheet dữ liệu cho biểu đồ

    return path

def _write_summary_sheet(writer, params, result, formats):
    """Tạo trang tổng quan (Dashboard)."""
    sheet_name = "Dashboard"
    df_summary = pd.DataFrame() # Dùng sheet trống để vẽ
    df_summary.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]
    
    # --- Tiêu đề ---
    worksheet.merge_range('B2:I3', "BÁO CÁO TÍNH TOÁN KỸ THUẬT BĂNG TẢI", formats['title'])
    worksheet.merge_range('B5:C5', "Thông tin dự án", formats['subtitle'])
    worksheet.merge_range('F5:H5', "Các chỉ số hiệu suất chính (KPIs)", formats['subtitle'])

    # --- Thông tin dự án ---
    project_info = {
        "Tên dự án": params.project_name,
        "Khách hàng": params.client,
        "Người thiết kế": params.designer,
        "Ngày tạo": datetime.now().strftime('%d/%m/%Y'),
    }
    row = 6
    for key, value in project_info.items():
        worksheet.write(f'B{row}', key, formats['label'])
        worksheet.write(f'C{row}', value, formats['value'])
        row += 1

    # --- KPIs ---
    kpis = {
        "Công suất động cơ (kW)": result.motor_power_kw,
        "Hệ số an toàn (SF)": result.safety_factor,
        "% Cường độ đai": result.belt_strength_utilization,
        "% Tiết diện băng": result.capacity_utilization,
        "Tổng CAPEX (USD)": result.cost_capital_total,
        "Tổng OPEX/năm (USD)": result.op_cost_total_per_year,
    }
    row = 6
    for key, value in kpis.items():
        worksheet.write(f'F{row}', key, formats['label'])
        
        # Áp dụng định dạng có điều kiện
        cell_format = formats['value']
        if "Công suất" in key: cell_format = formats['number']
        if "CAPEX" in key or "OPEX" in key: cell_format = formats['money']
        if "%" in key: cell_format = formats['percent']
            
        if key == "Hệ số an toàn (SF)":
            if value >= 8: cell_format = formats['status_ok']
            elif value >= 6: cell_format = formats['status_warn']
            else: cell_format = formats['status_danger']
        
        if key == "% Cường độ đai":
            if value <= 80: cell_format = formats['status_ok']
            else: cell_format = formats['status_danger']

        worksheet.write(f'G{row}', value, cell_format)
        row += 1
    
    # --- Biểu đồ ---
    # 1. Biểu đồ phân tích chi phí (CAPEX)
    cost_chart = writer.book.add_chart({'type': 'pie'})
    cost_chart.set_title({'name': 'Phân tích Chi phí Đầu tư (CAPEX)'})
    cost_chart.add_series({
        'name': 'Cost Breakdown',
        'categories': '=Cost_Analysis!$B$4:$B$8',
        'values':     '=Cost_Analysis!$C$4:$C$8',
        'data_labels': {'percentage': True, 'leader_lines': True},
    })
    worksheet.insert_chart('B13', cost_chart, {'x_offset': 5, 'y_offset': 5})

    # 2. Biểu đồ phân bố lực căng
    tension_chart = writer.book.add_chart({'type': 'line'})
    tension_chart.set_title({'name': 'Phân bố Lực căng dọc Băng tải'})
    tension_chart.set_x_axis({'name': 'Khoảng cách (m)'})
    tension_chart.set_y_axis({'name': 'Lực căng (N)'})
    
    num_data_points = len(result.distances_m)
    tension_chart.add_series({
        'name': 'Lực căng tổng',
        'categories': f'=Data_Profile!$A$2:$A${num_data_points + 1}',
        'values':     f'=Data_Profile!$B$2:$B${num_data_points + 1}',
        'line':       {'color': '#2980B9', 'width': 2},
    })
    tension_chart.set_legend({'position': 'none'})
    worksheet.insert_chart('F13', tension_chart, {'x_offset': 5, 'y_offset': 5, 'x_scale': 1.2, 'y_scale': 1.0})

    worksheet.set_column('B:B', 25)
    worksheet.set_column('C:C', 30)
    worksheet.set_column('F:F', 25)
    worksheet.set_column('G:G', 20)

def _write_inputs_sheet(writer, params, formats):
    """Tạo sheet Thông số đầu vào."""
    sheet_name = "Input_Parameters"
    
    # Chuyển đổi object thành dictionary để dễ xử lý
    params_dict = vars(params)
    
    df_inputs = pd.DataFrame(list(params_dict.items()), columns=["Thông số", "Giá trị"])
    df_inputs.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
    
    worksheet = writer.sheets[sheet_name]
    worksheet.write('A1', 'THÔNG SỐ THIẾT KẾ ĐẦU VÀO', formats['subtitle'])
    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:B', 35)
    
    # Áp dụng định dạng header
    for col_num, value in enumerate(df_inputs.columns.values):
        worksheet.write(1, col_num, value, formats['header'])

def _write_results_sheet(writer, result, formats):
    """Tạo sheet Kết quả Tính toán Chi tiết."""
    sheet_name = "Detailed_Results"
    
    result_groups = {
        "Tải trọng & Lưu lượng": {
            "Lưu lượng khối (kg/s)": result.mass_flow_rate,
            "Lưu lượng thực tế (tấn/giờ)": result.Qt_effective_tph,
            "Tải trọng vật liệu (kg/m)": result.material_load_kgpm,
            "Khối lượng băng (kg/m)": result.belt_weight_kgpm,
            "KL bộ phận chuyển động (kg/m)": result.moving_parts_weight_kgpm,
            "Tổng tải trọng động (kg/m)": result.total_load_kgpm,
        },
        "Lực cản & Lực căng": {
            "Tổng lực cản ma sát (N)": result.friction_force,
            "Lực nâng vật liệu (N)": result.lift_force,
            "Lực căng hiệu dụng F_U (N)": result.effective_tension,
            "Lực căng nhánh căng T1 (N)": result.T1,
            "Lực căng nhánh chùng T2 (N)": result.T2,
            "Lực căng lớn nhất T_max (N)": result.max_tension,
        },
        "Công suất & Hiệu suất": {
            "Công suất yêu cầu tại tang (kW)": result.required_power_kw,
            "Hiệu suất truyền động (%)": result.drive_efficiency_percent,
            "Công suất động cơ đề xuất (kW)": result.motor_power_kw,
        }
    }

    if result.drive_distribution_method:
        result_groups["Truyền động kép"] = {
            "Phương pháp phân phối": result.drive_distribution_method,
            "Lực vòng Puly 1 (kgf)": result.Fp1,
            "Lực vòng Puly 2 (kgf)": result.Fp2,
            "Lực căng lớn nhất F11 (N)": result.F11,
        }
        
    df = pd.DataFrame() # Sheet trống
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]
    
    row = 0
    for group_title, data in result_groups.items():
        worksheet.merge_range(row, 0, row, 1, group_title, formats['group_header'])
        row += 1
        for key, value in data.items():
            worksheet.write(row, 0, key, formats['label'])
            cell_format = formats['number'] if isinstance(value, (int, float)) else formats['value']
            worksheet.write(row, 1, value, cell_format)
            row += 1
        row += 1 # Thêm một dòng trống giữa các nhóm

    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:B', 25)

def _write_structural_sheet(writer, result, formats):
    """Tạo sheet Đề xuất Cấu trúc."""
    sheet_name = "Structural_Recs"
    
    pulley_data = result.recommended_pulley_diameters_mm
    idler_data = {
        "Khoảng cách con lăn nhánh tải (m)": result.recommended_idler_spacing_m.get('Nhánh tải (đề xuất)', 0),
        "Khoảng cách con lăn nhánh về (m)": result.recommended_idler_spacing_m.get('Nhánh về (đề xuất)', 0),
        "Khoảng cách chuyển tiếp tối thiểu (m)": result.transition_distance_m,
    }

    df = pd.DataFrame() # Sheet trống
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    worksheet = writer.sheets[sheet_name]

    # Bảng Puly
    worksheet.merge_range('A1:B1', 'Đường kính Puly đề xuất (Mục 8.1, PDF)', formats['group_header'])
    row = 2
    for key, value in pulley_data.items():
        worksheet.write(row, 0, key, formats['label'])
        worksheet.write(row, 1, f"{value:.0f} mm", formats['value'])
        row += 1
    
    # Bảng Con lăn
    row += 1
    worksheet.merge_range(f'A{row}:B{row}', 'Khoảng cách Con lăn đề xuất (Mục 8.2, PDF)', formats['group_header'])
    row += 1
    for key, value in idler_data.items():
        worksheet.write(row, 0, key, formats['label'])
        worksheet.write(row, 1, value, formats['number'])
        row += 1

    worksheet.set_column('A:A', 35)
    worksheet.set_column('B:B', 25)
    
def _write_cost_sheet(writer, result, formats):
    """Tạo sheet Phân tích Chi phí."""
    sheet_name = "Cost_Analysis"
    
    cost_data = [
        ("Chi phí Đầu tư (CAPEX)", "Chi phí băng tải", result.cost_belt),
        (None, "Chi phí con lăn", result.cost_idlers),
        (None, "Chi phí kết cấu", result.cost_structure),
        (None, "Chi phí truyền động", result.cost_drive),
        (None, "Chi phí khác (lắp đặt,...)", result.cost_others),
        (None, "TỔNG CHI PHÍ ĐẦU TƯ", result.cost_capital_total),
        ("Chi phí Vận hành/Năm (OPEX)", "Chi phí năng lượng/năm", result.op_cost_energy_per_year),
        (None, "Chi phí bảo trì/năm", result.op_cost_maintenance_per_year),
        (None, "TỔNG CHI PHÍ VẬN HÀNH/NĂM", result.op_cost_total_per_year),
    ]
    
    df_cost = pd.DataFrame(cost_data, columns=["Phân loại", "Hạng mục", "Giá trị (USD)"])
    df_cost.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1)
    
    worksheet = writer.sheets[sheet_name]
    worksheet.write('A1', 'PHÂN TÍCH CHI PHÍ (ƯỚC TÍNH)', formats['subtitle'])
    
    # Áp dụng định dạng
    for col_num, value in enumerate(df_cost.columns.values):
        worksheet.write(1, col_num, value, formats['header'])
    
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 20, formats['money'])
    
    # Merge các cell Phân loại
    worksheet.merge_range('A3:A8', 'Chi phí Đầu tư (CAPEX)', formats['label'])
    worksheet.merge_range('A9:A11', 'Chi phí Vận hành/Năm (OPEX)', formats['label'])
    
def _write_data_profile_sheet(writer, result, formats):
    """Tạo sheet ẩn chứa dữ liệu cho biểu đồ."""
    sheet_name = "Data_Profile"
    
    profile_data = {
        "Distance (m)": result.distances_m,
        "Tension (N)": result.tension_profile,
    }
    df_profile = pd.DataFrame(profile_data)
    df_profile.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Ẩn sheet này đi cho gọn gàng
    worksheet = writer.sheets[sheet_name]
    worksheet.hide()
