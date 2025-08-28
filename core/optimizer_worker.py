# core/optimizer_worker.py
# -*- coding: utf-8 -*-

from PySide6.QtCore import QObject, Signal, Slot
import time

from core.models import ConveyorParameters
from core.optimizer.models import OptimizerSettings
from core.optimizer.optimizer import Optimizer


class OptimizerWorker(QObject):
    """Worker to run the optimization process in a separate thread."""

    finished = Signal(list)   # Emits list of DesignCandidate results
    progress = Signal(int)    # Emits progress percentage
    status = Signal(str)      # Emits status updates to UI status bar

    def __init__(self, base_params: ConveyorParameters, opt_settings: OptimizerSettings):
        super().__init__()
        self.base_params = base_params
        self.opt_settings = opt_settings
        self.status_queue: list[tuple[str, int]] = []
        self.current_status_index = 0

    def _add_status_message(self, message: str, delay_ms: int = 0):
        self.status_queue.append((message, delay_ms))

    def _emit_status_sequence_blocking(self):
        """Emit queued status messages sequentially with delays.
        This uses blocking sleep so messages appear even when the worker thread
        is about to start a long-running computation.
        """
        for idx in range(self.current_status_index, len(self.status_queue)):
            message, delay = self.status_queue[idx]
            self.status.emit(message)
            if delay and delay > 0:
                time.sleep(delay / 1000.0)
        self.current_status_index = len(self.status_queue)

    @Slot()
    def run(self):
        """Execute the optimization."""
        try:
            # Reset queue
            self.status_queue.clear()
            self.current_status_index = 0

            # Start messages
            self._add_status_message("🚀 Bắt đầu quá trình tối ưu hóa nâng cao...", 0)

            # Validate input
            if not self.base_params:
                raise ValueError("Tham số cơ bản không hợp lệ")
            if not self.opt_settings:
                raise ValueError("Cài đặt tối ưu hóa không hợp lệ")

            self._add_status_message("🔧 Khởi tạo bộ tối ưu hóa...", 800)
            optimizer = Optimizer(self.base_params, self.opt_settings)

            # Choose GA parameters based on problem complexity
            base_width = self.base_params.B_mm
            capacity = self.base_params.Qt_tph

            if capacity > 2000 or base_width > 1600:
                population_size = 150
                generations = 60
                self._add_status_message("📈 Bài toán RẤT PHỨC TẠP - Sử dụng dân số lớn (150) và nhiều thế hệ (60)", 1000)
            elif capacity > 1000 or base_width > 1200:
                population_size = 120
                generations = 50
                self._add_status_message("📊 Bài toán phức tạp - Sử dụng dân số lớn (120) và nhiều thế hệ (50)", 1000)
            elif capacity > 500 or base_width > 800:
                population_size = 80
                generations = 40
                self._add_status_message("⚖️ Bài toán trung bình - Sử dụng dân số vừa phải (80) và thế hệ cân bằng (40)", 1000)
            else:
                population_size = 60
                generations = 35
                self._add_status_message("✅ Bài toán đơn giản - Dân số tối ưu (60) và thế hệ phù hợp (35)", 1000)

            # Mutation rate based on generations
            if generations > 50:
                mutation_rate = 0.20
            elif generations > 40:
                mutation_rate = 0.18
            elif generations > 30:
                mutation_rate = 0.15
            else:
                mutation_rate = 0.12

            # Tournament size based on population
            if population_size > 100:
                tournament_size = max(5, min(12, population_size // 15))
            else:
                tournament_size = max(3, min(8, population_size // 10))

            # Crossover rate based on complexity
            if capacity > 1000 or base_width > 1200:
                crossover_rate = 0.85
            else:
                crossover_rate = 0.80

            # Elitism
            elitism_count = 0  # Let optimizer decide internally if needed

            self._add_status_message(
                f"🧬 Đang chạy thuật toán di truyền với {generations} thế hệ, {population_size} cá thể...",
                1200,
            )
            self._add_status_message(
                f"⚙️ Tham số nâng cao: Tỉ lệ đột biến gen={mutation_rate:.2f}, Kích thước quần thể={tournament_size}, Tỉ lệ lai ghép={crossover_rate:.2f}",
                1500,
            )

            # Show the sequence before the heavy run
            self._emit_status_sequence_blocking()

            # Run optimization
            results = optimizer.run(
                generations=generations,
                population_size=population_size,
                mutation_rate=mutation_rate,
                tournament_size=tournament_size,
                elitism_count=elitism_count,
                crossover_rate=crossover_rate,
            )

            # Report results
            if results:
                msg = f"🎉 Tối ưu hóa hoàn tất! Tìm thấy {len(results)} giải pháp hợp lệ."
                self._add_status_message(msg, 2000)
                self.status.emit(msg)
                self.finished.emit(results[:10])
            else:
                msg = "❌ Không tìm thấy giải pháp hợp lệ nào."
                self._add_status_message(msg, 2000)
                self.status.emit(msg)
                self.finished.emit([])

        except Exception as e:
            import traceback
            error_msg = f"⛔ Lỗi tối ưu hóa: {str(e)}"
            print(f"OptimizerWorker Error: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            self.status.emit(error_msg)
            self.finished.emit([])

