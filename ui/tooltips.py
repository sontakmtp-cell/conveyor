# title="ui/tooltips.py" contentType="text/python"
# -*- coding: utf-8 -*-
"""
Chú thích siêu dễ hiểu, không cần tài liệu.
Mỗi tooltip nói ngắn gọn: đây là gì, dùng để làm gì.
"""

from __future__ import annotations
from typing import Any

HTML = {
    # Thông tin dự án
    "edt_project_name": "<b>Tên dự án</b><br>Tên gọi để nhận ra công việc của bạn.",
    "edt_designer": "<b>Người thiết kế</b><br>Ai đang làm bản tính này.",
    "edt_client": "<b>Khách hàng</b><br>Làm cho ai.",
    "edt_location": "<b>Vị trí lắp đặt</b><br>Băng tải đặt ở đâu.",

    # Vật liệu
    "cbo_material": "<b>Vật liệu</b><br>Thứ băng tải chở: cát, than, đá… Chọn đúng loại.",
    "spn_density": "<b>Nặng nhẹ (tấn/m³)</b><br>Vật liệu nặng thì băng phải khỏe hơn.",
    "spn_particle": "<b>Kích thước hạt (mm)</b><br>Hạt to dễ rơi và mài mòn. Hạt càng to càng nên chạy chậm.",
    "spn_angle": "<b>Góc đống vật liệu (°)</b><br>Vật liệu “đứng” dốc được bao nhiêu. Dốc hơn thì chở được nhiều hơn.",
    "spn_temp": "<b>Nhiệt độ vật liệu (°C)</b><br>Nóng quá có thể hỏng băng. Kiểm tra giới hạn khi số cao.",
    "chk_abrasive": "<b>Mài mòn</b><br>Vật liệu cứng, cọ mạnh. Cần băng bền hơn.",
    "chk_corrosive": "<b>Ăn mòn</b><br>Có thể làm gỉ, mục. Cần chọn vật liệu chống ăn mòn.",
    "chk_dusty": "<b>Bụi</b><br>Dễ bay bụi. Nên che chắn và dùng con lăn kín bụi.",

    # Vận hành
    "cbo_standard": "<b>Tiêu chuẩn tính</b><br>Cách tính toán chính: CEMA, DIN, ISO.",
    "spn_capacity": "<b>Lưu lượng (tấn/giờ)</b><br>Băng cần chở được bao nhiêu trong 1 giờ.",
    "spn_length": "<b>Chiều dài L (m)</b><br>Băng dài bao nhiêu. Dài thì ma sát nhiều hơn.",
    "spn_height": "<b>Độ cao H (m)</b><br>Nâng vật liệu lên cao bao nhiêu. Cao hơn cần nhiều lực hơn.",
    "spn_incl": "<b>Góc nghiêng (°)</b><br>Dốc lên hay dốc xuống bao nhiêu. Dốc quá dễ trượt rơi.",
    "spn_speed": "<b>Tốc độ băng (m/s)</b><br>🚀 <b>GIỜ ĐÂY TÍNH TỰ ĐỘNG!</b><br>Hệ thống sẽ tự động tính tốc độ tối ưu dựa trên:<br>• Lưu lượng yêu cầu<br>• Bề rộng băng được chọn<br>• Loại vật liệu và kích thước hạt<br><br>Không cần nhập tay - kết quả sẽ hiển thị trong tab 'Tổng quan'",
    "spn_hours": "<b>Giờ chạy mỗi ngày</b><br>Dùng để ước tính điện năng.",

    # Băng
    "cbo_width": "<b>Bề rộng B (mm)</b><br>Băng rộng thì chở được nhiều hơn nhưng tốn năng lượng hơn.",
    "cbo_belt_type": (
        "<b>Loại băng</b><br>"
        "Chọn vật liệu và kết cấu băng phù hợp môi trường và tải trọng.<br><br>"
        "<u>EP (Vải Polyester)</u><br>"
        "• Ưu: Bền kéo tốt, giãn ít, chịu ẩm khá, giá hợp lý.<br>"
        "• Nhược: Không cứng bằng dây thép, nhiệt cao quá sẽ kém.<br><br>"
        "<u>NN (Vải Nylon)</u><br>"
        "• Ưu: Dẻo, chịu va đập tốt, chạy êm với con lăn thưa vừa.<br>"
        "• Nhược: Độ giãn lớn hơn EP, cần cân chỉnh căng băng tốt.<br><br>"
        "<u>ST (Dây thép)</u><br>"
        "• Ưu: Cực bền, giãn rất thấp, hợp băng rất dài/tải nặng, tang to.<br>"
        "• Nhược: Giá cao, cần con lăn và lắp đặt chuẩn hơn.<br><br>"
        "<u>PVC</u><br>"
        "• Ưu: Nhẹ, chống ẩm/ăn mòn tốt, phù hợp thực phẩm/kho sạch.<br>"
        "• Nhược: Nhiệt độ giới hạn thấp, tải nặng không bằng EP/ST.<br><br>"
        "<u>Cao su</u><br>"
        "• Ưu: Bám tốt, chống mài mòn, dùng ngoài trời ổn.<br>"
        "• Nhược: Nặng hơn, có thể kỵ dầu/hóa chất mạnh."
    ),
    "spn_thickness": "<b>Độ dày băng (mm)</b><br>Dày thì bền hơn nhưng nặng hơn.",
    "cbo_trough": (
        "<b>Góc máng (°)</b><br>"
        "Ba con lăn tạo thành “máng”. Máng sâu (góc lớn) chứa được nhiều hơn, "
        "nhưng cần băng, con lăn và căn chỉnh tốt hơn. "
        "Thường chọn: 20°–35° cho băng cỡ vừa; 35°–45° cho băng lớn."
    ),
    "spn_surcharge": (
        "<b>Góc chất tải (°)</b><br>"
        "Độ nhọn/bè của đống vật liệu trên băng. <b>Luôn bằng góc nghiêng tự nhiên</b> của vật liệu. "
        "Góc lớn thì chở nhiều hơn nhưng dễ văng rơi nếu chạy nhanh. "
        "Thường 20°–30° cho vật liệu chảy tốt; 30°–35° cho vật liệu góc nghỉ lớn."
    ),
    "spn_carrying": "<b>KC con lăn tải (m)</b><br>Gần thì êm, xa thì tiết kiệm. Đừng quá thưa nếu băng nặng.",
    "spn_return": "<b>KC con lăn về (m)</b><br>Nhánh về nhẹ, có thể thưa hơn nhánh tải.",

    # Truyền động
    "cbo_drive": "<b>Kiểu đặt động cơ</b><br>Đầu, đuôi, giữa, hay hai động cơ. Ảnh hưởng cách kéo băng.",
    # --- [BẮT ĐẦU NÂNG CẤP] ---
    "cbo_dual_drive_ratio": (
        "<b>Tỷ lệ phân phối lực (Truyền động kép)</b><br>"
        "Chọn cách chia sẻ tải trọng giữa 2 động cơ.<br><br>"
        "<u>Phân phối lý thuyết:</u><br>"
        "• Tính toán Fp1, Fp2 theo công thức (23) trong PDF. Tối ưu để giảm lực căng lớn nhất, nhưng có thể yêu cầu 2 động cơ công suất khác nhau.<br><br>"
        "<u>Phân phối đều (50/50):</u><br>"
        "• Chia đều tổng lực vòng cho 2 động cơ (Fp1 = Fp2). Đơn giản, dùng 2 động cơ giống hệt nhau.<br><br>"
        "<u>Phân phối 2/1 (66/33):</u><br>"
        "• Động cơ chính (Puly 1) chịu 2/3 tải, động cơ phụ (Puly 2) chịu 1/3. Dùng khi cần một động cơ chính mạnh hơn."
    ),
    # --- [KẾT THÚC NÂNG CẤP] ---
    
    # --- [BẮT ĐẦU NÂNG CẤP HỘP SỐ MANUAL] ---
    "gearbox_ratio_mode_select": (
        "<b>Chế độ hộp số</b><br>"
        "Chọn cách xác định tỉ số truyền của hộp số giảm tốc.<br><br>"
        "<u>Tự động tính toán:</u><br>"
        "• Phần mềm tự động chọn từ danh sách tỉ số chuẩn (5, 8, 10, 12.5, 15, 20, 25, 30...)<br>"
        "• Tối ưu đa mục tiêu: sai số vận tốc → tổng răng nhỏ → i_s gần 1.9 → pitch nhỏ/nhẹ<br><br>"
        "<u>Chỉ định:</u><br>"
        "• Người dùng nhập tỉ số cụ thể (ví dụ: 12.5)<br>"
        "• Thuật toán sẽ tính và chọn nhông-xích dựa trên i_g này<br>"
        "• Nếu i_s_target ngoài dải [1.2, 3.0], sẽ clamp về giới hạn gần nhất"
    ),
    "gearbox_ratio_input": (
        "<b>Tỉ số hộp số</b><br>"
        "Nhập tỉ số truyền của hộp số giảm tốc khi chọn chế độ Chỉ định.<br><br>"
        "<u>Giá trị hợp lý:</u><br>"
        "• Thường từ 5 đến 100<br>"
        "• Tỉ số cao = giảm tốc nhiều = motor quay nhanh, puly quay chậm<br>"
        "• Tỉ số thấp = giảm tốc ít = motor và puly quay gần nhau<br><br>"
        "<u>Gợi ý nhanh:</u><br>"
        "• 5, 8, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 80, 100"
    ),
    # --- [KẾT THÚC NÂNG CẤP HỘP SỐ MANUAL] ---
    
    "spn_eta_m": "<b>Hiệu suất động cơ</b><br>Gần 1 là tốt.",
    "spn_eta_g": "<b>Hiệu suất hộp số</b><br>Cao thì đỡ tốn điện.",
    "spn_mu": """
    <div style="font-family: Segoe UI; font-size: 13px; max-width: 450px;">
        <h4 style="margin-bottom: 5px; color: #005A9E;">Hệ số ma sát (μ) giữa băng tải và puly</h4>
        <p style="margin-top: 0px; font-style: italic;">
            Hệ số ma sát quyết định khả năng truyền lực kéo từ puly đến dây băng.
        </p>
        <table border="1" style="width:100%; border-collapse: collapse; font-size: 12px;">
            <thead style="background-color: #E8F4FD; text-align: center;">
                <tr>
                    <th style="padding: 4px;">Bề mặt puly</th>
                    <th style="padding: 4px;">Điều kiện</th>
                    <th style="padding: 4px;">Hệ số ma sát (μ)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td rowspan="3" style="padding: 4px;"><strong>Puly thép trơn</strong></td>
                    <td style="padding: 4px;">Bẩn và ươt</td>
                    <td style="text-align: center; padding: 4px;">0.1</td>
                </tr>
                <tr>
                    <td style="padding: 4px;">Ẩm</td>
                    <td style="text-align: center; padding: 4px;">0.10-0.20</td>
                </tr>
                <tr>
                    <td style="padding: 4px;">Khô</td>
                    <td style="text-align: center; padding: 4px;">0.30</td>
                </tr>
                <tr>
                    <td rowspan="3" style="padding: 4px;"><strong>Puly bọc cao su</strong></td>
                    <td style="padding: 4px;">Bẩn và ướt</td>
                    <td style="text-align: center; padding: 4px;">0.2</td>
                </tr>
                <tr>
                    <td style="padding: 4px;">Ẩm</td>
                    <td style="text-align: center; padding: 4px;">0.2 - 0.3</td>
                </tr>
                <tr>
                    <td style="padding: 4px;">Khô</td>
                    <td style="text-align: center; padding: 4px;">0.35</td>
                </tr>
            </tbody>
        </table>
        <p style="margin-top: 8px; font-size: 12px;">
            <strong>Khuyến nghị:</strong> Sử dụng puly bọc cao su để tăng hệ số ma sát, đặc biệt quan trọng trong điều kiện vận hành ẩm ướt hoặc có nguy cơ trượt băng.
        </p>
    </div>
    """,
    "spn_wrap": "<b>Góc ôm tang (°)</b><br>Ôm nhiều thì bám tốt.",
    "spn_Kt": "<b>Hệ số khởi động</b><br>Cho biết cần dư lực khi khởi động.",

    # Môi trường
    "spn_amb": "<b>Nhiệt độ môi trường (°C)</b><br>Nóng quá máy móc dễ mệt. Kiểm tra khi số cao.",
    "spn_hum": "<b>Độ ẩm (%)</b><br>Ẩm có thể gây trượt, gỉ sét.",
    "spn_alt": "<b>Độ cao (m)</b><br>Lên cao không khí loãng, motor có thể yếu hơn chút.",
    "chk_dusty_env": "<b>Môi trường bụi</b><br>Nên che chắn và tăng bảo trì.",
    "chk_corr_env": "<b>Môi trường ăn mòn</b><br>Cần vật liệu chống gỉ, chống mục.",
    "chk_ex": "<b>Khu vực dễ nổ</b><br>Dùng thiết bị đạt chuẩn chống nổ.",
    
    # --- [BẮT ĐẦU NÂNG CẤP TRUYỀN ĐỘNG] ---
    "motor_rpm_input": (
        "<b>Tốc độ động cơ (vòng/phút)</b><br>"
        "Tốc độ quay của động cơ điện.<br><br>"
        "<u>Giá trị phổ biến:</u><br>"
        "• 1450 rpm: Động cơ 4 cực, phổ biến nhất, hiệu suất cao<br>"
        "• 2900 rpm: Động cơ 2 cực, tốc độ cao, công suất cao<br>"
        "• 750 rpm: Động cơ 8 cực, tốc độ thấp, mô-men xoắn cao<br>"
        "• 1000, 1500, 1800, 2200, 3000 rpm: Các tốc độ khác<br><br>"
        "<u>Lưu ý:</u><br>"
        "• Tốc độ cao = giảm tốc nhiều = hộp số tỉ số lớn<br>"
        "• Tốc độ thấp = giảm tốc ít = hộp số tỉ số nhỏ"
    ),
    # --- [KẾT THÚC NÂNG CẤP TRUYỀN ĐỘNG] ---
    
    # --- [BẮT ĐẦU NÂNG CẤP TỐC ĐỘ ĐẦU RA ĐỘNG CƠ] ---
    "motor_output_rpm": (
        "<b>Tốc độ đầu ra động cơ (vòng/phút)</b><br>"
        "Tốc độ quay của trục đầu ra động cơ sau khi qua hộp số giảm tốc.<br><br>"
        "<u>Công thức tính:</u><br>"
        "• Tốc độ đầu ra = Tốc độ động cơ ÷ Tỉ số hộp số<br>"
        "• Ví dụ: 1450 rpm ÷ 15 = 96.7 rpm<br><br>"
        "<u>Ý nghĩa:</u><br>"
        "• Tốc độ này sẽ quay trực tiếp puly dẫn động<br>"
        "• Càng thấp thì puly quay càng chậm, băng tải chạy càng chậm<br>"
        "• Phải phù hợp với vận tốc băng tải yêu cầu"
    ),
    # --- [KẾT THÚC NÂNG CẤP TỐC ĐỘ ĐẦU RA ĐỘNG CƠ] ---
}

def _set_tt(obj: Any, name: str, text: str) -> None:
    try:
        w = getattr(obj, name, None)
        if w is not None and hasattr(w, "setToolTip"):
            w.setToolTip(text)
    except Exception:
        pass

def apply_tooltips(inputs_panel: Any) -> None:
    for key, text in HTML.items():
        _set_tt(inputs_panel, key, text)

