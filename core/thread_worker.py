# -*- coding: utf-8 -*-
from PySide6.QtCore import QThread, Signal
from .models import ConveyorParameters, CalculationResult
from .validators import validate_input_ranges, validate_material_compatibility
from .engine import calculate

class CalculationThread(QThread):
    progress_updated = Signal(int)
    calculation_finished = Signal(object)
    status_updated = Signal(str)

    def __init__(self, params: ConveyorParameters):
        super().__init__()
        self.params = params

    def run(self):
        res = CalculationResult()
        try:
            self.status_updated.emit("Đang kiểm tra dữ liệu đầu vào...")
            warns = []
            warns += validate_input_ranges(self.params)
            warns += validate_material_compatibility(self.params)
            self.progress_updated.emit(15)

            self.status_updated.emit("Đang tính toán tải trọng và tiết diện...")
            self.progress_updated.emit(45)

            res = calculate(self.params)
            res.warnings.extend(warns)

            self.progress_updated.emit(90)
            self.status_updated.emit("Đang hoàn thiện kết quả...")

            self.progress_updated.emit(100)
            self.status_updated.emit("Tính toán hoàn tất.")
        except Exception as e:
            res.warnings.append(f"Lỗi tính toán: {e}")
        self.calculation_finished.emit(res)
