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
            
            # Kiểm tra tham số đầu vào
            if not self.base_params:
                raise ValueError("Tham số cơ bản không hợp lệ")
            
            if not self.opt_settings:
                raise ValueError("Cài đặt tối ưu hóa không hợp lệ")
            
            self.status.emit("🔧 Khởi tạo bộ tối ưu hóa...")
            optimizer = Optimizer(self.base_params, self.opt_settings)
            
            # Cải thiện BƯỚC 6: Điều chỉnh parameters trong OptimizerWorker
            # Tính toán parameters dựa trên độ phức tạp của bài toán
            base_width = self.base_params.B_mm
            capacity = self.base_params.Qt_tph
            
            # Điều chỉnh population_size dựa trên độ phức tạp
            if capacity > 1000 or base_width > 1200:
                # Bài toán phức tạp: tăng population và generations
                population_size = 80
                generations = 40
                self.status.emit("📊 Bài toán phức tạp - Sử dụng population lớn và nhiều thế hệ")
            elif capacity > 500 or base_width > 800:
                # Bài toán trung bình
                population_size = 60
                generations = 35
                self.status.emit("📊 Bài toán trung bình - Sử dụng tham số cân bằng")
            else:
                # Bài toán đơn giản: giảm để tăng tốc độ
                population_size = 40
                generations = 30
                self.status.emit("📊 Bài toán đơn giản - Sử dụng tham số tối ưu cho tốc độ")
            
            # Điều chỉnh mutation_rate dựa trên số thế hệ
            if generations > 35:
                mutation_rate = 0.15  # Tăng mutation cho nhiều thế hệ
            elif generations > 25:
                mutation_rate = 0.12  # Mutation vừa phải
            else:
                mutation_rate = 0.10  # Mutation thấp cho ít thế hệ
            
            # Điều chỉnh tournament_size dựa trên population_size
            tournament_size = max(3, min(8, population_size // 10))
            
            # Điều chỉnh elitism_count (sẽ được tự động tính trong optimizer)
            elitism_count = 0  # Để optimizer tự động tính toán
            
            self.status.emit(f"⚡ Đang chạy thuật toán di truyền với {generations} thế hệ, {population_size} cá thể...")
            self.status.emit(f"🔧 Tham số: mutation_rate={mutation_rate:.2f}, tournament_size={tournament_size}")
            
            results = optimizer.run(
                generations=generations, 
                population_size=population_size,
                mutation_rate=mutation_rate,
                tournament_size=tournament_size,
                elitism_count=elitism_count
            )
            
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
