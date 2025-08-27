# Đặt trong module mới: core/optimizer/models.py
from dataclasses import dataclass, field
from core.models import CalculationResult

@dataclass
class DesignCandidate:
    # --- Gen (Các biến quyết định) ---
    belt_width_mm: int
    # belt_speed_mps: float  # Đã loại bỏ - tốc độ sẽ được tính tự động từ bề rộng và lưu lượng
    belt_type_name: str
    gearbox_ratio: float
    chain_spec_designation: str # Mã định danh của xích

    # --- Kết quả đánh giá ---
    is_valid: bool = False # Thiết kế có hợp lệ không (ví dụ: có tìm được bộ truyền động không)
    fitness_score: float = float('inf') # Điểm E, càng thấp càng tốt
    calculation_result: CalculationResult | None = None # Kết quả chi tiết từ core.engine
    invalid_reasons: list = field(default_factory=list) # Danh sách lý do không hợp lệ

@dataclass
class OptimizerSettings:
    # --- Trọng số (từ 0.0 đến 1.0) ---
    w_cost: float = 0.6 # Ưu tiên chi phí
    w_power: float = 0.3 # Ưu tiên tiết kiệm năng lượng
    w_safety: float = 0.1 # Ưu tiên độ bền
    w_velocity_error: float = 0.1 # Ưu tiên sai số vận tốc thấp

    # --- Ràng buộc (ví dụ) ---
    max_budget_usd: float | None = None # Chi phí đầu tư tối đa
    min_belt_safety_factor: float = 8.0 # Hệ số an toàn băng tối thiểu
    max_velocity_error_percent: float = 10.0 # Sai số vận tốc tối đa chấp nhận được (%)