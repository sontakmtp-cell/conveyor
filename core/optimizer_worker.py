# core/optimizer_worker.py
# -*- coding: utf-8 -*-

from PySide6.QtCore import QObject, Signal, Slot
from core.models import ConveyorParameters
from core.optimizer.models import OptimizerSettings
from core.optimizer.optimizer import Optimizer

class OptimizerWorker(QObject):
    """Worker to run the optimization process in a separate thread."""
    finished = Signal(list)  # Emits list of DesignCandidate results
    progress = Signal(int)   # Emits progress percentage
    status = Signal(str)   # Emits status updates

    def __init__(self, base_params: ConveyorParameters, opt_settings: OptimizerSettings):
        super().__init__()
        self.base_params = base_params
        self.opt_settings = opt_settings

    @Slot()
    def run(self):
        """Execute the optimization."""
        try:
            self.status.emit("🚀 Bắt đầu quá trình tối ưu hóa nâng cao...")
            optimizer = Optimizer(self.base_params, self.opt_settings)
            
            # Chạy tối ưu với tham số giảm để tránh quá tải
            results = optimizer.run(generations=30, population_size=50)
            
            if results:
                self.status.emit(f"✅ Tối ưu hóa hoàn tất! Tìm thấy {len(results)} giải pháp hợp lệ.")
                self.finished.emit(results)
            else:
                self.status.emit("⚠️ Không tìm thấy giải pháp hợp lệ nào.")
                self.finished.emit([])
                
        except Exception as e:
            import traceback
            error_msg = f"❌ Lỗi tối ưu hóa: {str(e)}"
            print(f"OptimizerWorker Error: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            self.status.emit(error_msg)
            self.finished.emit([])
