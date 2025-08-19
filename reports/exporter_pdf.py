# reports/exporter_pdf.py
# -*- coding: utf-8 -*-
"""
Module xuất báo cáo PDF chuyên nghiệp cho Phần mềm Tính toán Băng tải.
Bố cục được thiết kế lại hoàn toàn để mang lại giao diện hiện đại, rõ ràng và chuyên sâu.
Bao gồm trang bìa, header/footer đồng nhất, các mục phân tích chi tiết và biểu đồ.
"""

import os
import tempfile
from datetime import datetime
import matplotlib.figure
from fpdf import FPDF, XPos, YPos

# --- CÁC HẰNG SỐ VÀ MÀU SẮC ---
COLOR_PRIMARY = (41, 128, 185)    # Blue
COLOR_SECONDARY = (52, 73, 94)     # Dark Blue/Grey
COLOR_LIGHT_GREY = (236, 240, 241) # Light Grey Background
COLOR_DARK_GREY = (127, 140, 141)  # Grey Text
COLOR_SUCCESS = (39, 174, 96)      # Green
COLOR_WARNING = (243, 156, 18)     # Orange
COLOR_DANGER = (192, 57, 43)       # Red

# --- CÁC HÀM TIỆN ÍCH ---
def get_resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cả khi chạy trực tiếp và khi đóng gói."""
    try:
        # PyInstaller tạo một thư mục tạm thời và lưu đường dẫn trong sys._MEIPASS
        import sys
        base_path = sys._MEIPASS
        # Khi đóng gói, các tài nguyên nằm cùng cấp với exe
        if relative_path.startswith('ui/'):
            relative_path = relative_path[3:]
        return os.path.join(base_path, relative_path)
    except Exception:
        # Chạy ở chế độ phát triển
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..'))
        return os.path.join(project_root, relative_path)

def extract_matplotlib_figure(obj):
    """Trích xuất đối tượng Figure từ các nguồn có thể có."""
    if isinstance(obj, matplotlib.figure.Figure):
        return obj
    if hasattr(obj, "savefig"):
        return obj
    for attr in ["fig", "figure", "plot", "chart"]:
        if hasattr(obj, attr):
            cand = getattr(obj, attr)
            if isinstance(cand, matplotlib.figure.Figure) or hasattr(cand, "savefig"):
                return cand
    return None

# --- LỚP PDF CHUYÊN NGHIỆP ---
class ProfessionalPDFExporter(FPDF):
    def __init__(self, params, result, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = params
        self.result = result
        self.project_name = getattr(params, 'project_name', 'Dự án Băng tải')
        self.logo_path = get_resource_path("ui/images/logo.png") # Giả định có logo
        
        self.set_auto_page_break(auto=True, margin=20)
        self.alias_nb_pages()
        self._setup_fonts()

    def _setup_fonts(self):
        """Thêm các font chữ DejaVu để hỗ trợ tiếng Việt tốt nhất."""
        try:
            fonts_dir = get_resource_path("reports/fonts")
            self.add_font("DejaVu", "", os.path.join(fonts_dir, "DejaVuSans.ttf"))
            self.add_font("DejaVu", "B", os.path.join(fonts_dir, "DejaVuSans-Bold.ttf"))
            self.add_font("DejaVu", "I", os.path.join(fonts_dir, "DejaVuSans-Oblique.ttf"))
            self.set_font("DejaVu", size=10)
        except Exception:
            # Fallback to standard fonts if DejaVu is not found
            self.set_font("Helvetica", size=10)

    def header(self):
        """Tạo header cho mỗi trang (trừ trang bìa)."""
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(*COLOR_SECONDARY)
        
        # Logo
        if os.path.exists(self.logo_path):
            self.image(self.logo_path, x=10, y=8, h=8)
        
        # Tên dự án
        self.cell(0, 10, self.project_name, align='C')
        
        # Tên phần mềm
        self.set_xy(0, 10)
        self.cell(0, 10, "Conveyor Calculator Professional", align='R')
        
        # Dòng kẻ
        self.set_draw_color(*COLOR_PRIMARY)
        self.line(10, 20, 200, 20)
        self.ln(15)

    def footer(self):
        """Tạo footer cho mỗi trang."""
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(*COLOR_DARK_GREY)
        
        # Thông tin bản quyền
        self.cell(0, 10, "Báo cáo được tạo bởi Phần mềm Tính toán Băng tải Công nghiệp", align='L')
        
        # Số trang
        self.set_xy(0, -15)
        self.cell(0, 10, f"Trang {self.page_no()} / {{nb}}", align='R')

    def draw_cover_page(self):
        """Vẽ trang bìa báo cáo."""
        self.add_page()
        
        # Nền trang bìa
        self.set_fill_color(*COLOR_PRIMARY)
        self.rect(0, 0, 210, 80, 'F')
        
        # Logo
        if os.path.exists(self.logo_path):
            self.image(self.logo_path, x=15, y=15, h=25)
            
        # Tiêu đề chính
        self.set_y(45)
        self.set_font("DejaVu", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "BÁO CÁO TÍNH TOÁN KỸ THUẬT", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_font("DejaVu", "B", 18)
        self.cell(0, 10, "HỆ THỐNG BĂNG TẢI", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        # Thông tin dự án
        self.set_y(100)
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(*COLOR_SECONDARY)
        self.cell(0, 15, self.project_name, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        self.set_y(140)
        self.set_font("DejaVu", "", 11)
        self.set_text_color(*COLOR_DARK_GREY)
        
        info_data = [
            ("Khách hàng:", getattr(self.params, 'client', 'N/A')),
            ("Người thiết kế:", getattr(self.params, 'designer', 'N/A')),
            ("Vị trí:", getattr(self.params, 'location', 'N/A')),
            ("Ngày tạo báo cáo:", datetime.now().strftime('%d/%m/%Y %H:%M')),
        ]
        
        col_widths = (40, 130)
        for label, value in info_data:
            self.set_x((210 - sum(col_widths)) / 2)
            self.set_font(style="B")
            self.cell(col_widths[0], 8, label)
            self.set_font(style="")
            self.multi_cell(col_widths[1], 8, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Footer trang bìa
        self.set_y(250)
        self.set_font("DejaVu", "I", 9)
        self.set_text_color(*COLOR_DARK_GREY)
        self.multi_cell(0, 5, "Tài liệu này chứa thông tin kỹ thuật phục vụ cho mục đích thiết kế và đánh giá. "
                              "Các kết quả cần được kiểm tra và phê duyệt bởi kỹ sư có chuyên môn trước khi áp dụng vào thực tế.", align='C')

    def _draw_section_title(self, title: str):
        """Vẽ tiêu đề cho một mục mới."""
        self.ln(10)
        self.set_font("DejaVu", "B", 14)
        self.set_fill_color(*COLOR_PRIMARY)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"   {title}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def _draw_key_value_table(self, data: dict, title: str = None):
        """Vẽ bảng 2 cột dạng Key-Value."""
        if title:
            self.set_font("DejaVu", "B", 11)
            self.set_text_color(*COLOR_SECONDARY)
            self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2)

        self.set_font("DejaVu", "", 10)
        self.set_text_color(0, 0, 0)
        col_widths = (80, 100)
        line_height = 8

        for key, value in data.items():
            self.set_fill_color(*COLOR_LIGHT_GREY)
            self.cell(col_widths[0], line_height, f" {key}", border=1, fill=True)
            self.set_fill_color(255, 255, 255)
            self.multi_cell(col_widths[1], line_height, f" {value}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def draw_executive_summary(self):
        """Mục 1: Tóm tắt cho Lãnh đạo."""
        self.add_page()
        self._draw_section_title("1. TÓM TẮT DÀNH CHO LÃNH ĐẠO")
        
        summary_text = (
            "Báo cáo này trình bày các kết quả tính toán và đề xuất kỹ thuật cho hệ thống băng tải dựa trên các thông số thiết kế đã cung cấp. "
            "Các thông số chính bao gồm công suất động cơ, loại băng, lực căng và các cấu trúc liên quan đã được xác định "
            "để đảm bảo hệ thống vận hành hiệu quả và an toàn. Các phân tích chi tiết được trình bày trong các mục tiếp theo."
        )
        self.set_font("DejaVu", "", 10)
        self.set_text_color(0,0,0)
        self.multi_cell(0, 5, summary_text)
        self.ln(5)

        summary_data = {
            "Bề rộng băng đề xuất": f"{self.params.B_mm} mm",
            "Tốc độ băng vận hành": f"{self.params.V_mps} m/s",
            "Công suất động cơ yêu cầu": f"{self.result.motor_power_kw:.2f} kW",
            "Lực căng lớn nhất trên băng (T_max)": f"{self.result.max_tension:,.0f} N",
            "Hệ số an toàn của băng (SF)": f"{self.result.safety_factor:.2f}",
            "Tổng chi phí đầu tư (CAPEX) ước tính": f"${self.result.cost_capital_total:,.0f} USD"
        }
        self._draw_key_value_table(summary_data, "Các thông số kỹ thuật chính")

    def draw_input_parameters(self):
        """Mục 2: Thông số Thiết kế Đầu vào."""
        self.add_page()
        self._draw_section_title("2. THÔNG SỐ THIẾT KẾ ĐẦU VÀO")
        
        p = self.params
        input_groups = {
            "Thông tin chung": {
                "Tiêu chuẩn tính toán": p.calculation_standard,
                "Vật liệu vận chuyển": p.material,
                "Giờ vận hành mỗi ngày": f"{p.operating_hours} giờ/ngày",
            },
            "Đặc tính vật liệu": {
                "Khối lượng riêng": f"{p.density_tpm3} tấn/m³",
                "Kích thước hạt lớn nhất": f"{p.particle_size_mm} mm",
                "Góc nghỉ tự nhiên": f"{p.angle_repose_deg}°",
                "Nhiệt độ vật liệu": f"{p.material_temp_c}°C",
            },
            "Thông số hình học & vận hành": {
                "Lưu lượng yêu cầu (Qt)": f"{p.Qt_tph} tấn/giờ",
                "Chiều dài băng tải (L)": f"{p.L_m} m",
                "Chiều cao nâng (H)": f"{p.H_m} m",
                "Góc nghiêng băng tải": f"{p.inclination_deg}°",
            },
            "Cấu hình băng và truyền động": {
                "Loại băng tải": p.belt_type,
                "Góc máng con lăn": p.trough_angle_label,
                "Loại truyền động": p.drive_type,
                "Góc ôm tang dẫn động": f"{p.wrap_deg}°",
            }
        }

        for title, data in input_groups.items():
            self._draw_key_value_table(data, title)
            self.ln(5)

    def draw_detailed_results(self):
        """Mục 3: Kết quả Tính toán Chi tiết."""
        self.add_page()
        self._draw_section_title("3. KẾT QUẢ TÍNH TOÁN CHI TIẾT")

        r = self.result
        result_groups = {
            "Tải trọng trên băng": {
                "Tải trọng vật liệu (q_G)": f"{r.material_load_kgpm:.2f} kg/m",
                "Khối lượng băng (q_B)": f"{r.belt_weight_kgpm:.2f} kg/m",
                "KL các bộ phận quay (q_Ro, q_Ru)": f"{r.moving_parts_weight_kgpm:.2f} kg/m",
                "Tổng tải trọng động": f"{r.total_load_kgpm:.2f} kg/m",
            },
            "Lực cản và Lực căng": {
                "Tổng lực cản ma sát": f"{r.friction_force:,.0f} N",
                "Lực nâng vật liệu": f"{r.lift_force:,.0f} N",
                "Lực căng hiệu dụng (F_U)": f"{r.effective_tension:,.0f} N",
                "Lực căng nhánh chùng (T2)": f"{r.T2:,.0f} N",
                "Lực căng nhánh căng (T1)": f"{r.T1:,.0f} N",
            },
            "Công suất": {
                "Công suất yêu cầu tại tang (P_req)": f"{r.required_power_kw:.2f} kW",
                "Hiệu suất tổng thể truyền động": f"{r.drive_efficiency_percent:.1f} %",
                "Công suất động cơ đề xuất (P_motor)": f"{r.motor_power_kw:.2f} kW",
            }
        }
        
        # Thêm mục truyền động kép nếu có
        if r.drive_distribution_method:
            result_groups["Phân tích truyền động kép"] = {
                "Phương pháp phân phối lực": r.drive_distribution_method,
                "Lực vòng Puly 1 (Fp1)": f"{r.Fp1:,.1f} kgf",
                "Lực vòng Puly 2 (Fp2)": f"{r.Fp2:,.1f} kgf",
                "Lực căng lớn nhất (F11)": f"{r.F11:,.0f} N",
            }

        for title, data in result_groups.items():
            self._draw_key_value_table(data, title)
            self.ln(5)

    def draw_technical_analysis(self):
        """Mục 4: Phân tích Kỹ thuật và Khuyến nghị."""
        self.add_page()
        self._draw_section_title("4. PHÂN TÍCH KỸ THUẬT & KHUYẾN NGHỊ")
        
        r = self.result
        
        # Phân tích
        self.set_font("DejaVu", "B", 11)
        self.set_text_color(*COLOR_SECONDARY)
        self.cell(0, 10, "Đánh giá các chỉ số hiệu suất chính", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

        analysis_data = {
            "Hệ số an toàn băng (SF)": (f"{r.safety_factor:.2f}", r.safety_factor >= 6.0),
            "% sử dụng cường độ đai": (f"{r.belt_strength_utilization:.1f}%", r.belt_strength_utilization <= 80.0),
            "% sử dụng tiết diện băng": (f"{r.capacity_utilization:.1f}%", r.capacity_utilization <= 95.0),
        }
        
        self.set_font("DejaVu", "", 10)
        for key, (value, is_ok) in analysis_data.items():
            self.set_fill_color(*COLOR_LIGHT_GREY)
            self.cell(80, 8, f" {key}", border=1, fill=True)
            self.set_text_color(*COLOR_SUCCESS if is_ok else COLOR_DANGER)
            self.set_font(style="B")
            self.multi_cell(100, 8, f" {value} {'(Đạt)' if is_ok else '(Cần xem xét)'}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font(style="")
            self.set_text_color(0,0,0)
        
        # Cảnh báo
        if r.warnings:
            self.ln(5)
            self.set_font("DejaVu", "B", 11)
            self.set_text_color(*COLOR_WARNING)
            self.cell(0, 10, "Cảnh báo kỹ thuật", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("DejaVu", "", 10)
            self.set_text_color(0,0,0)
            for warning in r.warnings:
                self.multi_cell(0, 5, f"• {warning}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Khuyến nghị
        if r.recommendations:
            self.ln(5)
            self.set_font("DejaVu", "B", 11)
            self.set_text_color(*COLOR_SUCCESS)
            self.cell(0, 10, "Đề xuất & Khuyến nghị", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font("DejaVu", "", 10)
            self.set_text_color(0,0,0)
            for rec in r.recommendations:
                self.multi_cell(0, 5, f"• {rec}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def draw_cost_analysis(self):
        """Mục 5: Phân tích Chi phí."""
        self.add_page()
        self._draw_section_title("5. PHÂN TÍCH CHI PHÍ (ƯỚC TÍNH)")
        
        r = self.result
        capex_data = {
            "Chi phí băng tải": f"${r.cost_belt:,.0f}",
            "Chi phí con lăn": f"${r.cost_idlers:,.0f}",
            "Chi phí kết cấu": f"${r.cost_structure:,.0f}",
            "Chi phí truyền động": f"${r.cost_drive:,.0f}",
            "Chi phí khác (lắp đặt,...)": f"${r.cost_others:,.0f}",
            "TỔNG CHI PHÍ ĐẦU TƯ (CAPEX)": f"${r.cost_capital_total:,.0f}",
        }
        self._draw_key_value_table(capex_data, "Chi phí Đầu tư ban đầu (CAPEX)")
        self.ln(5)
        
        opex_data = {
            "Chi phí năng lượng/năm": f"${r.op_cost_energy_per_year:,.0f}",
            "Chi phí bảo trì/năm (ước tính 2%)": f"${r.op_cost_maintenance_per_year:,.0f}",
            "TỔNG CHI PHÍ VẬN HÀNH/NĂM (OPEX)": f"${r.op_cost_total_per_year:,.0f}",
        }
        self._draw_key_value_table(opex_data, "Chi phí Vận hành hằng năm (OPEX)")

    def draw_structural_recommendations(self):
        """Mục 6: Đề xuất Cấu trúc."""
        self.add_page()
        self._draw_section_title("6. ĐỀ XUẤT CẤU TRÚC (THEO PDF)")

        r = self.result
        pulley_data = {
            "Puly dẫn động/đầu (Loại A)": f"{r.recommended_pulley_diameters_mm.get('Puly dẫn động/đầu (Loại A)', 0):.0f} mm",
            "Puly căng/đuôi (Loại B)": f"{r.recommended_pulley_diameters_mm.get('Puly căng/đuôi (Loại B)', 0):.0f} mm",
            "Puly dẫn hướng (Loại C)": f"{r.recommended_pulley_diameters_mm.get('Puly dẫn hướng (Loại C)', 0):.0f} mm",
        }
        self._draw_key_value_table(pulley_data, "Đường kính Puly tối thiểu đề xuất (Mục 8.1)")
        self.ln(5)

        idler_data = {
            "Khoảng cách con lăn nhánh tải": f"{r.recommended_idler_spacing_m.get('Nhánh tải (đề xuất)', 0):.2f} m",
            "Khoảng cách con lăn nhánh về": f"{r.recommended_idler_spacing_m.get('Nhánh về (đề xuất)', 0):.2f} m",
            "Khoảng cách chuyển tiếp tối thiểu": f"{r.transition_distance_m:.3f} m",
        }
        self._draw_key_value_table(idler_data, "Khoảng cách Con lăn đề xuất (Mục 8.2)")

    def draw_chart_appendix(self, fig_obj):
        """Mục 7: Phụ lục Biểu đồ."""
        fig = extract_matplotlib_figure(fig_obj)
        if not fig:
            return

        self.add_page()
        self._draw_section_title("PHỤ LỤC: BIỂU ĐỒ PHÂN BỐ LỰC CĂNG")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor=COLOR_LIGHT_GREY)
            
            # Canh giữa hình ảnh
            img_width = 180 # mm
            x_pos = (210 - img_width) / 2
            self.image(tmpfile.name, x=x_pos, w=img_width)
            
        # Dọn dẹp file tạm
        os.unlink(tmpfile.name)
        
# --- HÀM XUẤT PDF CHÍNH ---
def export_pdf_report(output_path, params_obj, result_obj=None, fig=None, logo_path=None):
    """
    Hàm chính để tạo và lưu báo cáo PDF chuyên nghiệp.
    """
    if not result_obj:
        raise ValueError("Đối tượng kết quả (result_obj) không được để trống.")

    pdf = ProfessionalPDFExporter(params_obj, result_obj)
    
    # Gán logo nếu có
    if logo_path and os.path.exists(logo_path):
        pdf.logo_path = logo_path
        
    # 1. Vẽ trang bìa
    pdf.draw_cover_page()
    
    # 2. Vẽ các mục nội dung
    pdf.draw_executive_summary()
    pdf.draw_input_parameters()
    pdf.draw_detailed_results()
    pdf.draw_technical_analysis()
    pdf.draw_structural_recommendations()
    pdf.draw_cost_analysis()
    
    # 3. Vẽ biểu đồ
    if fig:
        pdf.draw_chart_appendix(fig)

    # 4. Lưu file
    pdf.output(output_path)
    return output_path
