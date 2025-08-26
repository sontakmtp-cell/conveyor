# -*- coding: utf-8 -*-
from PySide6.QtCore import QThread, Signal
from .models import ConveyorParameters, CalculationResult
from .validators import validate_input_ranges, validate_material_compatibility
from .engine import calculate
import traceback
import logging

class CalculationThread(QThread):
    progress_updated = Signal(int)
    calculation_finished = Signal(object)
    status_updated = Signal(str)

    def __init__(self, params: ConveyorParameters):
        super().__init__()
        self.params = params

    def run(self):
        try:
            self.status_updated.emit("Đang kiểm tra dữ liệu đầu vào...")
            print(f"DEBUG: Bắt đầu tính toán với params: {self.params}")
            
            warns = []
            warns += validate_input_ranges(self.params)
            warns += validate_material_compatibility(self.params)
            print(f"DEBUG: Validation warnings: {warns}")
            self.progress_updated.emit(15)

            self.status_updated.emit("Đang tính toán tải trọng và tiết diện...")
            self.progress_updated.emit(45)

            print("DEBUG: Gọi hàm calculate()...")
            res = calculate(self.params)
            print(f"DEBUG: Kết quả từ calculate(): {res}")
            print(f"DEBUG: Các giá trị chính: motor_power_kw={res.motor_power_kw}, required_power_kw={res.required_power_kw}")
            
            # Thêm validation warnings vào kết quả
            res.warnings.extend(warns)

            self.progress_updated.emit(90)
            self.status_updated.emit("Đang hoàn thiện kết quả...")

            self.progress_updated.emit(100)
            self.status_updated.emit("Tính toán hoàn tất.")
            print(f"DEBUG: Kết quả cuối cùng: {res}")
            
        except Exception as e:
            print(f"DEBUG: Exception xảy ra: {e}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            
            # Tạo kết quả rỗng với warning về lỗi
            res = CalculationResult()
            res.warnings.append(f"Lỗi tính toán: {e}")
            logging.error(f"Lỗi tính toán: {e}", exc_info=True)
        
        print(f"DEBUG: Emit kết quả: {res}")
        self.calculation_finished.emit(res)
