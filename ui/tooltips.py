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
    "spn_speed": "<b>Tốc độ băng (m/s)</b><br>Băng chạy nhanh hay chậm. Nhanh chở nhiều nhưng dễ văng rơi.",
    "spn_hours": "<b>Giờ chạy mỗi ngày</b><br>Dùng để ước tính điện năng.",

    # Băng
    "cbo_width": "<b>Bề rộng B (mm)</b><br>Băng rộng thì chở được nhiều hơn nhưng tốn hơn.",
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
        "Độ nhọn/bè của đống vật liệu trên băng. Phụ thuộc vào vật liệu (góc nghỉ tự nhiên). "
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
    "spn_eta_m": "<b>Hiệu suất động cơ</b><br>Gần 1 là tốt.",
    "spn_eta_g": "<b>Hiệu suất hộp số</b><br>Cao thì đỡ tốn điện.",
    "spn_mu": "<b>Độ bám băng–tang</b><br>Bám tốt thì ít trượt.",
    "spn_wrap": "<b>Góc ôm tang (°)</b><br>Ôm nhiều thì bám tốt.",
    "spn_Kt": "<b>Hệ số khởi động</b><br>Cho biết cần dư lực khi khởi động.",

    # Môi trường
    "spn_amb": "<b>Nhiệt độ môi trường (°C)</b><br>Nóng quá máy móc dễ mệt. Kiểm tra khi số cao.",
    "spn_hum": "<b>Độ ẩm (%)</b><br>Ẩm có thể gây trượt, gỉ sét.",
    "spn_alt": "<b>Độ cao (m)</b><br>Lên cao không khí loãng, motor có thể yếu hơn chút.",
    "chk_dusty_env": "<b>Môi trường bụi</b><br>Nên che chắn và tăng bảo trì.",
    "chk_corr_env": "<b>Môi trường ăn mòn</b><br>Cần vật liệu chống gỉ, chống mục.",
    "chk_ex": "<b>Khu vực dễ nổ</b><br>Dùng thiết bị đạt chuẩn chống nổ.",
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

