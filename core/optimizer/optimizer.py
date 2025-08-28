# core/optimizer/optimizer.py
import random
import copy
import math
import sys # Added for flushing print statements
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

from .models import DesignCandidate, OptimizerSettings
from core.models import ConveyorParameters, CalculationResult
from core.engine import calculate
from core.specs import (
    STANDARD_WIDTHS, 
    ACTIVE_BELT_SPECS, 
    STANDARD_GEARBOX_RATIOS, 
    ACTIVE_CHAIN_SPECS,
    MATERIAL_DB,
    get_valid_ratings_for_belt_type,
)

# Cải thiện BƯỚC 6: Thiết lập logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class Optimizer:
    def __init__(self, base_params: ConveyorParameters, settings: OptimizerSettings):
        self.base_params = base_params
        self.settings = settings
        self.population: List[DesignCandidate] = []

    def run(self, generations: int = 50, population_size: int = 100, mutation_rate: float = 0.1, tournament_size: int = 5, elitism_count: int = 10, crossover_rate: float = 0.8) -> List[DesignCandidate]:
        """Chạy toàn bộ quá trình tối ưu hóa GA."""
        try:
            # Kiểm tra file CSV bảng tra tốc độ trước khi chạy GA
            csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hidden', 'Bang tra toc do bang tai.csv')
            if not os.path.exists(csv_path):
                print(f"Warning: Không tìm thấy file bảng tra tốc độ: {csv_path}")
                print("GA sẽ chạy với giá trị fallback an toàn (2.0 m/s)")
                print("Điều này có thể ảnh hưởng đến độ chính xác của tối ưu hóa")
            
            # Cải thiện BƯỚC 5: Điều chỉnh elitism_count dựa trên số generations và population_size
            if elitism_count <= 0:
                # Tính toán elitism_count dựa trên số generations và population_size
                if population_size >= 120:
                    # Dân số lớn: elitism cao hơn
                    if generations <= 30:
                        elitism_count = max(10, population_size // 12)
                    elif generations <= 50:
                        elitism_count = max(15, population_size // 10)
                    else:
                        elitism_count = max(20, population_size // 8)
                elif population_size >= 80:
                    # Dân số trung bình
                    if generations <= 30:
                        elitism_count = max(8, population_size // 15)
                    elif generations <= 50:
                        elitism_count = max(12, population_size // 12)
                    else:
                        elitism_count = max(15, population_size // 10)
                else:
                    # Dân số nhỏ
                    if generations <= 30:
                        elitism_count = max(5, population_size // 20)
                    elif generations <= 50:
                        elitism_count = max(8, population_size // 15)
                    else:
                        elitism_count = max(10, population_size // 10)
                
                print(f"Optimizer: Auto-adjusted elitism_count to {elitism_count} based on {generations} generations and {population_size} population")
            
            self._initialize_population(population_size)
        except Exception as e:
            print(f"Optimizer: Failed to initialize population: {e}")
            return []

        for gen in range(generations):
            print(f"Optimizer: Running Generation {gen + 1}/{generations}")
            print(f"Optimizer: Population size: {len(self.population)}, Valid candidates: {len([c for c in self.population if c.is_valid])}")
            
            try:
                self._evaluate_population()
            except Exception as e:
                print(f"Optimizer: Error evaluating generation {gen + 1}: {e}")
                continue

            self.population.sort(key=lambda c: c.fitness_score)

            # Lọc ra các cá thể không hợp lệ ra cuối danh sách
            valid_population = [c for c in self.population if c.is_valid]
            invalid_population = [c for c in self.population if not c.is_valid]
            
            if not valid_population:
                print("Optimizer: No valid candidates found in population. Stopping.")
                break

            # Hiển thị thông tin về thế hệ hiện tại
            best_fitness = valid_population[0].fitness_score if valid_population else float('inf')
            avg_fitness = sum(c.fitness_score for c in valid_population) / len(valid_population) if valid_population else 0
            print(f"Optimizer: Generation {gen + 1} - Best fitness: {best_fitness:.4f}, Avg fitness: {avg_fitness:.4f}")
            
            # CẢI THIỆN: Duy trì đa dạng dân số
            diversity_score = self._calculate_diversity(valid_population)
            print(f"Optimizer: Generation {gen + 1} diversity score: {diversity_score:.3f}")
            
            # Điều chỉnh mutation rate dựa trên diversity
            adaptive_mutation_rate = mutation_rate
            if diversity_score < 0.3:  # Đa dạng thấp
                adaptive_mutation_rate = min(0.3, mutation_rate * 1.5)  # Tăng mutation
                print(f"Optimizer: Low diversity detected, increasing mutation rate to {adaptive_mutation_rate:.3f}")
            elif diversity_score > 0.7:  # Đa dạng cao
                adaptive_mutation_rate = max(0.05, mutation_rate * 0.8)  # Giảm mutation
                print(f"Optimizer: High diversity detected, decreasing mutation rate to {adaptive_mutation_rate:.3f}")

            # Cải thiện BƯỚC 5: Điều chỉnh elitism_count động dựa trên chất lượng dân số
            current_elitism_count = min(elitism_count, len(valid_population))
            if len(valid_population) < elitism_count:
                print(f"Optimizer: Warning: Only {len(valid_population)} valid candidates, reducing elitism from {elitism_count} to {current_elitism_count}")
            
            new_generation = valid_population[:current_elitism_count] # Giữ lại cá thể tinh hoa

            # CẢI THIỆN: Sử dụng crossover_rate để quyết định có tạo con hay không
            while len(new_generation) < population_size:
                parent1 = self._tournament_selection(tournament_size, valid_population)
                parent2 = self._tournament_selection(tournament_size, valid_population)
                
                # Sử dụng crossover_rate để quyết định có tạo con hay không
                if random.random() < crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                    self._mutate(child1, adaptive_mutation_rate)
                    self._mutate(child2, adaptive_mutation_rate)
                    new_generation.extend([child1, child2])
                else:
                    # Nếu không crossover, chỉ mutate và copy parent
                    child1 = copy.deepcopy(parent1)
                    child2 = copy.deepcopy(parent2)
                    self._mutate(child1, adaptive_mutation_rate * 1.5)  # Tăng mutation cho copy
                    self._mutate(child2, adaptive_mutation_rate * 1.5)
                    new_generation.extend([child1, child2])
                
                # Kiểm tra nếu đã đủ dân số
                if len(new_generation) >= population_size:
                    break
            
            # Cắt tỉa dân số về đúng kích thước mong muốn
            self.population = new_generation[:population_size]

        # Đánh giá lại lần cuối và trả về kết quả tốt nhất
        print("Optimizer: Final evaluation...")
        self._evaluate_population()
        self.population.sort(key=lambda c: c.fitness_score)
        
        valid_results = [c for c in self.population if c.is_valid]
        print(f"Optimizer: Found {len(valid_results)} valid solutions.")
        
        # Hiển thị thống kê cuối cùng
        if valid_results:
            best_candidate = valid_results[0]
            print(f"Optimizer: Best solution - Width: {best_candidate.belt_width_mm}mm, "
                  f"Fitness: {best_candidate.fitness_score:.4f}, "
                  f"Belt Type: {best_candidate.belt_type_name}, "
                  f"Gearbox: {best_candidate.gearbox_ratio:.2f}")
            
            # Hiển thị top 5 solutions
            print("Optimizer: Top 5 solutions:")
            for i, candidate in enumerate(valid_results[:5]):
                print(f"  {i+1}. Width: {candidate.belt_width_mm}mm, "
                      f"Fitness: {candidate.fitness_score:.4f}, "
                      f"Belt: {candidate.belt_type_name}, "
                      f"Gearbox: {candidate.gearbox_ratio:.2f}")
        
        # CẢI THIỆN: Trả về kết quả đa dạng hơn
        if len(valid_results) >= 15:
            # Trả về top 15 thay vì chỉ top 10
            return valid_results[:15]
        elif len(valid_results) >= 10:
            return valid_results[:10]
        else:
            return valid_results  # Trả về tất cả nếu ít hơn 10

    def _initialize_population(self, size: int):
        """Tạo quần thể ban đầu một cách ngẫu nhiên."""
        self.population = []
        material_info = MATERIAL_DB.get(self.base_params.material, {})
        # v_max không được sử dụng trong logic khởi tạo, đã loại bỏ
        
        belt_types = list(ACTIVE_BELT_SPECS.keys())
        chain_designations = [cs.designation for cs in ACTIVE_CHAIN_SPECS if cs.designation]

        if not chain_designations:
            print("Optimizer: Warning: No chain specifications found. Using default.")
            chain_designations = ["05B", "08A", "16B"]  # Default chain designations

        # Cải thiện BƯỚC 5: Kiểm tra base_width có trong STANDARD_WIDTHS không
        base_width = self.base_params.B_mm
        if base_width not in STANDARD_WIDTHS:
            print(f"Optimizer: Warning: base_width {base_width}mm không có trong STANDARD_WIDTHS")
            print(f"STANDARD_WIDTHS available: {STANDARD_WIDTHS}")
            
            # Tìm bề rộng gần nhất trong STANDARD_WIDTHS
            closest_width = min(STANDARD_WIDTHS, key=lambda x: abs(x - base_width))
            print(f"Optimizer: Using closest standard width: {closest_width}mm (original: {base_width}mm)")
            base_width = closest_width

        # Tối ưu hóa BƯỚC 5: Tạo candidate "an toàn" với logic cải tiến
        safe_candidates = []
        
        # Candidate 1: Giữ nguyên tham số gốc (đã được validate)
        safe_candidates.append(DesignCandidate(
            belt_width_mm=base_width,
            belt_type_name=self.base_params.belt_type,
            gearbox_ratio=STANDARD_GEARBOX_RATIOS[0] if STANDARD_GEARBOX_RATIOS else 20.0,
            chain_spec_designation=chain_designations[0] if chain_designations else ""
        ))
        
        # Candidate 2: Tăng bề rộng (nếu có thể) - ưu tiên bề rộng lớn hơn gần nhất
        wider_widths = [w for w in STANDARD_WIDTHS if w > base_width]
        if wider_widths:
            # Chọn bề rộng lớn hơn gần nhất thay vì bất kỳ bề rộng nào
            next_wider = min(wider_widths)
            safe_candidates.append(DesignCandidate(
                belt_width_mm=next_wider,
                belt_type_name=self.base_params.belt_type,
                gearbox_ratio=STANDARD_GEARBOX_RATIOS[0] if STANDARD_GEARBOX_RATIOS else 20.0,
                chain_spec_designation=chain_designations[0] if chain_designations else ""
            ))
        
        # Candidate 3: Giảm bề rộng (nếu có thể) - ưu tiên bề rộng nhỏ hơn gần nhất
        narrower_widths = [w for w in STANDARD_WIDTHS if w < base_width]
        if narrower_widths:
            # Chọn bề rộng nhỏ hơn gần nhất thay vì bất kỳ bề rộng nào
            next_narrower = max(narrower_widths)
            safe_candidates.append(DesignCandidate(
                belt_width_mm=next_narrower,
                belt_type_name=self.base_params.belt_type,
                gearbox_ratio=STANDARD_GEARBOX_RATIOS[0] if STANDARD_GEARBOX_RATIOS else 20.0,
                chain_spec_designation=chain_designations[0] if chain_designations else ""
            ))

        # Candidate 4: Thêm candidate với gearbox ratio khác để tăng đa dạng
        if len(STANDARD_GEARBOX_RATIOS) > 1:
            # Chọn gearbox ratio khác với ratio đầu tiên
            alternative_gearbox = STANDARD_GEARBOX_RATIOS[1] if len(STANDARD_GEARBOX_RATIOS) > 1 else STANDARD_GEARBOX_RATIOS[0]
            safe_candidates.append(DesignCandidate(
                belt_width_mm=base_width,
                belt_type_name=self.base_params.belt_type,
                gearbox_ratio=alternative_gearbox,
                chain_spec_designation=chain_designations[0] if chain_designations else ""
            ))

        # Candidate 5: Thêm candidate với belt type khác nếu có nhiều loại
        if len(belt_types) > 1 and self.base_params.belt_type in belt_types:
            # Chọn belt type khác với type gốc
            current_index = belt_types.index(self.base_params.belt_type)
            alternative_belt_type = belt_types[(current_index + 1) % len(belt_types)]
            safe_candidates.append(DesignCandidate(
                belt_width_mm=base_width,
                belt_type_name=alternative_belt_type,
                gearbox_ratio=STANDARD_GEARBOX_RATIOS[0] if STANDARD_GEARBOX_RATIOS else 20.0,
                chain_spec_designation=chain_designations[0] if chain_designations else ""
            ))

        # MỞ RỘNG: Thêm các candidate với chain designation khác nhau
        if len(chain_designations) > 1:
            for i in range(min(3, len(chain_designations))):  # Tối đa 3 chain khác nhau
                if i < len(chain_designations):
                    safe_candidates.append(DesignCandidate(
                        belt_width_mm=base_width,
                        belt_type_name=self.base_params.belt_type,
                        gearbox_ratio=STANDARD_GEARBOX_RATIOS[0] if STANDARD_GEARBOX_RATIOS else 20.0,
                        chain_spec_designation=chain_designations[i]
                    ))

        # MỞ RỘNG: Thêm candidate với gearbox ratio trung bình
        if len(STANDARD_GEARBOX_RATIOS) > 2:
            mid_index = len(STANDARD_GEARBOX_RATIOS) // 2
            mid_gearbox = STANDARD_GEARBOX_RATIOS[mid_index]
            safe_candidates.append(DesignCandidate(
                belt_width_mm=base_width,
                belt_type_name=self.base_params.belt_type,
                gearbox_ratio=mid_gearbox,
                chain_spec_designation=chain_designations[0] if chain_designations else ""
            ))

        # Thêm các candidate an toàn vào đầu quần thể
        self.population.extend(safe_candidates)
        print(f"Optimizer: Added {len(safe_candidates)} optimized safe candidates based on original parameters")
        print(f"Optimizer: Safe candidates include: base_width={base_width}mm, alternative widths, gearbox ratios, belt types, and chain designations")

        # Tạo các candidate ngẫu nhiên cho phần còn lại với cải tiến
        remaining_size = size - len(safe_candidates)
        
        # CẢI THIỆN: Tạo candidate với chiến lược thông minh hơn
        for i in range(remaining_size):
            # Chiến lược 1: 40% khả năng chọn bề rộng gần với base_width
            if random.random() < 0.4:
                # Chọn từ 5 bề rộng gần nhất (tăng từ 3 lên 5)
                nearby_widths = sorted(STANDARD_WIDTHS, key=lambda x: abs(x - base_width))[:5]
                belt_width_mm = random.choice(nearby_widths)
            # Chiến lược 2: 30% khả năng chọn bề rộng trung bình
            elif random.random() < 0.7:
                # Chọn từ bề rộng trung bình
                mid_widths = sorted(STANDARD_WIDTHS)[len(STANDARD_WIDTHS)//4:3*len(STANDARD_WIDTHS)//4]
                belt_width_mm = random.choice(mid_widths)
            # Chiến lược 3: 30% khả năng chọn bề rộng bất kỳ
            else:
                belt_width_mm = random.choice(STANDARD_WIDTHS)
            
            # Chiến lược belt type: ưu tiên loại gốc
            if random.random() < 0.6:
                belt_type_name = self.base_params.belt_type
            else:
                belt_type_name = random.choice(belt_types)
            
            # Chiến lược gearbox: ưu tiên tỉ số gần với gốc
            if random.random() < 0.5:
                # Chọn từ 3 tỉ số gần nhất với tỉ số đầu tiên
                base_ratio = STANDARD_GEARBOX_RATIOS[0]
                nearby_ratios = sorted(STANDARD_GEARBOX_RATIOS, key=lambda x: abs(x - base_ratio))[:3]
                gearbox_ratio = random.choice(nearby_ratios)
            else:
                gearbox_ratio = random.choice(STANDARD_GEARBOX_RATIOS)
            
            # Chiến lược chain: ưu tiên loại gốc
            if random.random() < 0.6:
                chain_spec_designation = chain_designations[0]
            else:
                chain_spec_designation = random.choice(chain_designations)
            
            candidate = DesignCandidate(
                belt_width_mm=belt_width_mm,
                belt_type_name=belt_type_name,
                gearbox_ratio=gearbox_ratio,
                chain_spec_designation=chain_spec_designation
            )
            self.population.append(candidate)
        
        print(f"Optimizer: Initialized population with {len(self.population)} candidates ({len(safe_candidates)} optimized safe + {remaining_size} random with bias)")

    def _calculate_diversity(self, population: List[DesignCandidate]) -> float:
        """Tính toán độ đa dạng của dân số dựa trên các tham số."""
        if len(population) <= 1:
            return 0.0
        
        # Tính đa dạng dựa trên các tham số chính
        widths = [c.belt_width_mm for c in population]
        belt_types = [c.belt_type_name for c in population]
        gearbox_ratios = [c.gearbox_ratio for c in population]
        chain_designations = [c.chain_spec_designation for c in population]
        
        # Đa dạng bề rộng (normalized)
        width_diversity = len(set(widths)) / len(STANDARD_WIDTHS)
        
        # Đa dạng loại băng
        belt_diversity = len(set(belt_types)) / len(ACTIVE_BELT_SPECS)
        
        # Đa dạng tỉ số truyền
        gearbox_diversity = len(set(gearbox_ratios)) / len(STANDARD_GEARBOX_RATIOS)
        
        # Đa dạng chain
        chain_diversity = len(set(chain_designations)) / len([cs.designation for cs in ACTIVE_CHAIN_SPECS if cs.designation])
        
        # Tính trung bình có trọng số
        total_diversity = (width_diversity * 0.4 + belt_diversity * 0.2 + 
                          gearbox_diversity * 0.3 + chain_diversity * 0.1)
        
        return total_diversity

    def _evaluate_population(self):
        """Đánh giá từng cá thể trong quần thể, chuẩn hóa và tính điểm fitness."""
        # Bước 1: Chạy tính toán cho các cá thể chưa được đánh giá
        # Cải thiện BƯỚC 6: Giới hạn max_workers cho ThreadPool
        max_workers = min(os.cpu_count() or 8, 16)  # Giới hạn tối đa 16 workers
        logger.info(f"Using ThreadPool with max_workers={max_workers}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(self._evaluate_candidate, [c for c in self.population if c.calculation_result is None]))

        valid_candidates = [c for c in self.population if c.is_valid]
        if not valid_candidates:
            print("Optimizer: No valid candidates found in population. Trying to relax constraints...")
            
            # Thử làm mềm tiêu chí để tìm được ít nhất một số candidate
            relaxed_candidates = []
            for c in self.population:
                if hasattr(c, 'calculation_result') and c.calculation_result:
                    # Kiểm tra safety factor với ngưỡng an toàn cứng
                    safety_val = getattr(c.calculation_result, 'safety_factor', 0)
                    # Ngưỡng an toàn cứng: không bao giờ chấp nhận safety_factor < 4.0
                    hard_safety_threshold = 4.0
                    if safety_val >= hard_safety_threshold:
                        c.is_valid = True
                        relaxed_candidates.append(c)
                        print(f"Optimizer: Relaxed candidate {c} with safety factor {safety_val} (above hard threshold {hard_safety_threshold})")
            
            if relaxed_candidates:
                valid_candidates = relaxed_candidates
                print(f"Optimizer: Found {len(relaxed_candidates)} candidates after relaxing constraints (above hard safety threshold)")
            else:
                print("Optimizer: CRITICAL ERROR: No valid candidates found even after relaxing constraints.")
                print("Optimizer: All candidates have safety factor below hard threshold of 4.0.")
                print("Optimizer: This indicates serious issues with input parameters or design constraints.")
                print("Optimizer: Please check:")
                print("  - Material properties and density")
                print("  - Belt specifications and capacity")
                print("  - Safety requirements")
                print("  - Budget constraints")
                return

        # Bước 2: Tìm min/max cho việc chuẩn hóa (với kiểm tra an toàn)
        try:
            min_cost = min(getattr(c.calculation_result, 'cost_capital_total', float('inf')) for c in valid_candidates)
            max_cost = max(getattr(c.calculation_result, 'cost_capital_total', 0) for c in valid_candidates)
            min_power = min(getattr(c.calculation_result, 'required_power_kw', float('inf')) for c in valid_candidates)
            max_power = max(getattr(c.calculation_result, 'required_power_kw', 0) for c in valid_candidates)
            min_safety = min(getattr(c.calculation_result, 'safety_factor', float('inf')) for c in valid_candidates)
            max_safety = max(getattr(c.calculation_result, 'safety_factor', 0) for c in valid_candidates)
            
            # Cải tiến mới: Chuẩn hóa sai số vận tốc
            velocity_errors = []
            for c in valid_candidates:
                if hasattr(c.calculation_result, 'transmission_solution') and c.calculation_result.transmission_solution:
                    vel_err = getattr(c.calculation_result.transmission_solution, "velocity_error_percent", 0.0)
                    velocity_errors.append(vel_err)
            
            if velocity_errors:
                min_velocity_error = min(velocity_errors)
                max_velocity_error = max(velocity_errors)
                print(f"DEBUG: Velocity error range: [{min_velocity_error:.2f}%, {max_velocity_error:.2f}%]")
            else:
                min_velocity_error = max_velocity_error = 0.0

            # Cải thiện: Kiểm tra và xử lý các trường hợp đặc biệt
            logger.debug(f"Fitness calculation - Cost range: [{min_cost:.2f}, {max_cost:.2f}], "
                  f"Power range: [{min_power:.2f}, {max_power:.2f}], "
                  f"Safety range: [{min_safety:.2f}, {max_safety:.2f}]")
            
            # Kiểm tra nếu có giá trị vô cùng
            if min_cost == float('inf') or max_cost == 0:
                print("Warning: Invalid cost range detected, using fallback values")
                min_cost, max_cost = 0.0, 100000.0  # Fallback values
            
            if min_power == float('inf') or max_power == 0:
                print("Warning: Invalid power range detected, using fallback values")
                min_power, max_power = 0.0, 1000.0  # Fallback values
            
            if min_safety == float('inf') or max_safety == 0:
                print("Warning: Invalid safety range detected, using fallback values")
                min_safety, max_safety = 1.0, 20.0  # Fallback values

            # Bước 3: Tính điểm fitness cho từng cá thể hợp lệ
            for c in valid_candidates:
                cost = getattr(c.calculation_result, 'cost_capital_total', 0)
                power = getattr(c.calculation_result, 'required_power_kw', 0)
                safety = getattr(c.calculation_result, 'safety_factor', 0)

                # Cải thiện: Xử lý trường hợp đặc biệt khi tất cả giá trị giống nhau
                if max_cost > min_cost:
                    cost_norm = (cost - min_cost) / (max_cost - min_cost)
                else:
                    cost_norm = 0.5  # Giá trị trung bình nếu tất cả cost giống nhau
                
                if max_power > min_power:
                    power_norm = (power - min_power) / (max_power - min_power)
                else:
                    power_norm = 0.5  # Giá trị trung bình nếu tất cả power giống nhau
                
                # Cải thiện tính toán safety_norm để xử lý trường hợp max_safety == min_safety
                if max_safety > min_safety:
                    safety_norm = (safety - min_safety) / (max_safety - min_safety)
                else:
                    # Nếu tất cả candidate có safety giống nhau, ưu tiên safety cao hơn
                    target_safety = self.settings.min_belt_safety_factor
                    if target_safety > 0:
                        # Penalty nếu safety thấp hơn target, thưởng nếu cao hơn
                        if safety >= target_safety:
                            safety_norm = 0.0  # Không penalty cho safety tốt
                        else:
                            safety_norm = (target_safety - safety) / target_safety  # Penalty tăng dần
                    else:
                        safety_norm = 0.5  # Giá trị trung bình nếu không có target
                
                # Cải tiến mới: Chuẩn hóa sai số vận tốc
                velocity_error_norm = 0.0
                if hasattr(c.calculation_result, 'transmission_solution') and c.calculation_result.transmission_solution:
                    vel_err = getattr(c.calculation_result.transmission_solution, "velocity_error_percent", 0.0)
                    if max_velocity_error > min_velocity_error:
                        velocity_error_norm = (vel_err - min_velocity_error) / (max_velocity_error - min_velocity_error)
                    else:
                        velocity_error_norm = 0.0  # Không có sự khác biệt
                else:
                    velocity_error_norm = 1.0  # Penalty cao nếu không có transmission solution

                # Tính fitness cơ bản với cải thiện (tích hợp sai số vận tốc)
                base_fitness = (
                    self.settings.w_cost * cost_norm
                    + self.settings.w_power * power_norm
                    - self.settings.w_safety * safety_norm
                    + self.settings.w_velocity_error * velocity_error_norm
                )
                
                # Log chi tiết để debug (bao gồm sai số vận tốc)
                vel_err = getattr(c.calculation_result.transmission_solution, "velocity_error_percent", 0.0) if hasattr(c.calculation_result, 'transmission_solution') and c.calculation_result.transmission_solution else 0.0
                print(f"DEBUG: Candidate {c.belt_width_mm}mm - Cost: {cost:.2f} (norm: {cost_norm:.3f}), "
                      f"Power: {power:.2f} (norm: {power_norm:.3f}), "
                      f"Safety: {safety:.2f} (norm: {safety_norm:.3f}), "
                      f"Velocity Error: {vel_err:.2f}% (norm: {velocity_error_norm:.3f}), "
                      f"Base fitness: {base_fitness:.3f}")
                
                # Penalize các vấn đề (nhưng không loại bỏ hoàn toàn)
                penalty = 0.0
                if hasattr(c, 'invalid_reasons'):
                    for reason in c.invalid_reasons:
                        if "No transmission solution" in reason:
                            penalty += 0.5  # Tăng penalty từ 30% lên 50% cho không có transmission
                        elif "CẢNH BÁO" in reason or "⚠️" in reason:
                            penalty += 0.4  # Tăng penalty từ 20% lên 40% cho cảnh báo nghiêm trọng
                        elif "Warning:" in reason:
                            penalty += 0.3  # Tăng penalty từ 20% lên 30% cho warnings thông thường
                        elif "Cost too high" in reason:
                            penalty += 0.2  # Tăng penalty từ 10% lên 20% cho cost cao
                        elif "Safety factor too low" in reason:
                            penalty += 0.6  # Thêm penalty cao cho safety factor thấp
                        elif "vượt năng lực tiết diện" in reason or "bị khống chế bởi tiết diện" in reason:
                            penalty += 0.4  # Thêm penalty cho vấn đề tiết diện
                        elif "tốc độ" in reason.lower() and ("vượt quá" in reason or "cao" in reason):
                            penalty += 0.35  # Thêm penalty cho vấn đề tốc độ
                        elif "High velocity error" in reason:
                            penalty += 0.25  # Thêm penalty cho sai số vận tốc cao
                
                # Thêm penalty dựa trên safety factor nếu quá thấp
                if safety < self.settings.min_belt_safety_factor:
                    safety_penalty = (self.settings.min_belt_safety_factor - safety) / self.settings.min_belt_safety_factor
                    penalty += safety_penalty * 0.3  # Penalty tối đa 30% cho safety thấp
                
                final_fitness = base_fitness + penalty
                
                # Validation: Đảm bảo fitness score không vô cùng
                if not (float('-inf') < final_fitness < float('inf')):
                    print(f"Warning: Invalid fitness score detected for candidate {c.belt_width_mm}mm: {final_fitness}")
                    print(f"  Base fitness: {base_fitness}, Penalty: {penalty}")
                    # Sử dụng giá trị fallback an toàn
                    final_fitness = 10.0  # Giá trị fallback cao (fitness càng thấp càng tốt)
                
                c.fitness_score = final_fitness
                
                # Log penalty để debug
                if penalty > 0:
                    print(f"DEBUG: Candidate {c.belt_width_mm}mm - Penalty: {penalty:.3f}, Final fitness: {final_fitness:.3f}")
            
            # Log tổng kết fitness calculation
            fitness_scores = [c.fitness_score for c in valid_candidates]
            if fitness_scores:
                min_fitness = min(fitness_scores)
                max_fitness = max(fitness_scores)
                avg_fitness = sum(fitness_scores) / len(fitness_scores)
                print(f"DEBUG: Fitness summary - Min: {min_fitness:.3f}, Max: {max_fitness:.3f}, Avg: {avg_fitness:.3f}")
                
                # Sắp xếp candidates theo fitness để debug
                sorted_candidates = sorted(valid_candidates, key=lambda x: x.fitness_score)
                print(f"DEBUG: Top 3 candidates by fitness:")
                for i, candidate in enumerate(sorted_candidates[:3]):
                    vel_err = getattr(candidate.calculation_result.transmission_solution, "velocity_error_percent", 0.0) if hasattr(candidate.calculation_result, 'transmission_solution') and candidate.calculation_result.transmission_solution else 0.0
                    print(f"  {i+1}. Width: {candidate.belt_width_mm}mm, Fitness: {candidate.fitness_score:.3f}, Velocity Error: {vel_err:.2f}%")
                
        except Exception as e:
            print(f"Optimizer: Error in fitness calculation: {e}")
            # Fallback: gán fitness score đơn giản
            for c in valid_candidates:
                c.fitness_score = 1.0  # Default fitness score

    def _evaluate_candidate(self, candidate: DesignCandidate):
        """Chạy core.engine.calculate và kiểm tra tính hợp lệ cho một cá thể."""
        # Bước 1: Tính tốc độ theo CHÍNH bề rộng của candidate
        from core.optimize import calculate_belt_speed
        
        try:
            # Lấy thông số từ base_params
            capacity_tph = self.base_params.Qt_tph
            density_tpm3 = self.base_params.density_tpm3
            particle_mm = self.base_params.particle_size_mm
            material_name = self.base_params.material
            trough_angle_deg = 20.0  # Default, có thể cải thiện sau
            surcharge_angle_deg = getattr(self.base_params, 'surcharge_angle_deg', 20.0) or 20.0
            
            # Cải thiện: Luôn lấy material_characteristics từ base_params
            material_characteristics = {
                'is_abrasive': getattr(self.base_params, 'is_abrasive', True),
                'is_corrosive': getattr(self.base_params, 'is_corrosive', False),
                'is_dusty': getattr(self.base_params, 'is_dusty', True)
            }
            
            # Tối ưu/tính tốc độ theo CHÍNH bề rộng của candidate
            v_final, v_req, v_rec, area_m2, speed_warnings, max_speed_allowed = calculate_belt_speed(
                capacity_tph=capacity_tph,
                density_tpm3=density_tpm3,
                belt_width_mm=candidate.belt_width_mm,
                particle_mm=particle_mm,
                material_name=material_name,
                trough_angle_deg=trough_angle_deg,
                surcharge_angle_deg=surcharge_angle_deg,
                material_characteristics=material_characteristics  # Truyền material_characteristics
            )
            
            # Sử dụng bề rộng từ candidate và tốc độ được tính cho chính bề rộng đó
            params = copy.deepcopy(self.base_params)
            params.B_mm = candidate.belt_width_mm  # Giữ nguyên bề rộng từ candidate
            params.V_mps = v_final  # Sử dụng tốc độ được tính cho chính bề rộng này
            params.belt_type = candidate.belt_type_name
            # Ensure belt_rating_code matches the candidate belt type to use correct "cấu hình băng"
            try:
                base_code = getattr(self.base_params, 'belt_rating_code', None)
                current_code = getattr(params, 'belt_rating_code', None)
                # If belt type changed vs. base or rating code missing/empty, select a valid default for the type
                if (candidate.belt_type_name != getattr(self.base_params, 'belt_type', None)) or (not current_code):
                    valid_codes = []
                    try:
                        valid_codes = get_valid_ratings_for_belt_type(candidate.belt_type_name)
                    except Exception:
                        valid_codes = []
                    chosen = None
                    if candidate.belt_type_name == 'steel_cord':
                        # Prefer a common ST rating if available
                        for pref in ["ST-1600", "ST-1250", "ST-2000"]:
                            if pref in valid_codes:
                                chosen = pref
                                break
                    else:
                        # Prefer EP family as safe default
                        for pref in ["EP400/4", "EP500/4", "EP315/3"]:
                            if pref in valid_codes:
                                chosen = pref
                                break
                        if not chosen:
                            # fallback to first EP-like code if exists
                            chosen = next((c for c in valid_codes if str(c).startswith('EP')), None)
                    if not chosen and valid_codes:
                        chosen = valid_codes[0]
                    # If still nothing, keep base code if it looks compatible, else leave as-is
                    if chosen:
                        params.belt_rating_code = chosen
            except Exception:
                # Non-fatal: keep whatever rating the params currently carries
                pass
            # Chế độ manual để sử dụng gearbox_ratio của candidate
            params.gearbox_ratio_mode = "manual"
            params.gearbox_ratio_user = candidate.gearbox_ratio
            
            # Truyền gene xích vào engine nếu engine hỗ trợ
            if hasattr(params, "chain_selection_mode"):
                params.chain_selection_mode = "manual"
            if hasattr(params, "chain_spec_designation"):
                params.chain_spec_designation = candidate.chain_spec_designation
            
            # Lưu thông tin tốc độ vào candidate để debug
            candidate.auto_calculated_speed = v_final
            candidate.speed_warnings = speed_warnings
            
        except Exception as e:
            print(f"DEBUG ERROR: Failed to calculate auto speed for {candidate}: {e}")
            # Fallback: sử dụng tham số gốc với tốc độ an toàn
            params = copy.deepcopy(self.base_params)
            params.B_mm = candidate.belt_width_mm
            params.V_mps = 2.0  # Tốc độ mặc định an toàn (đã được cải thiện từ 5.0 m/s)
            params.belt_type = candidate.belt_type_name
            # Ensure belt_rating_code matches the candidate belt type in fallback path as well
            try:
                base_code = getattr(self.base_params, 'belt_rating_code', None)
                current_code = getattr(params, 'belt_rating_code', None)
                if (candidate.belt_type_name != getattr(self.base_params, 'belt_type', None)) or (not current_code):
                    valid_codes = []
                    try:
                        valid_codes = get_valid_ratings_for_belt_type(candidate.belt_type_name)
                    except Exception:
                        valid_codes = []
                    chosen = None
                    if candidate.belt_type_name == 'steel_cord':
                        for pref in ["ST-1600", "ST-1250", "ST-2000"]:
                            if pref in valid_codes:
                                chosen = pref
                                break
                    else:
                        for pref in ["EP400/4", "EP500/4", "EP315/3"]:
                            if pref in valid_codes:
                                chosen = pref
                                break
                        if not chosen:
                            chosen = next((c for c in valid_codes if str(c).startswith('EP')), None)
                    if not chosen and valid_codes:
                        chosen = valid_codes[0]
                    if chosen:
                        params.belt_rating_code = chosen
            except Exception:
                pass
            params.gearbox_ratio_mode = "manual"
            params.gearbox_ratio_user = candidate.gearbox_ratio
            
            # Truyền gene xích vào engine nếu engine hỗ trợ (fallback)
            if hasattr(params, "chain_selection_mode"):
                params.chain_selection_mode = "manual"
            if hasattr(params, "chain_spec_designation"):
                params.chain_spec_designation = candidate.chain_spec_designation

        try:
            print(f"DEBUG: Evaluating candidate {candidate}")
            result = calculate(params)
            # Propagate the belt rating code actually used into result and candidate for UI
            try:
                used_code = getattr(params, 'belt_rating_code', None)
                if used_code:
                    try:
                        setattr(result, 'belt_rating_code_used', used_code)
                    except Exception:
                        pass
                    try:
                        setattr(candidate, 'belt_rating_code', used_code)
                    except Exception:
                        pass
            except Exception:
                pass
            candidate.calculation_result = result
            print(f"DEBUG: Calculation completed for {candidate}")

            # Kiểm tra tính hợp lệ - Làm mềm hơn để tìm được giải pháp
            is_valid = True
            invalid_reasons = []
            
            # Kiểm tra transmission_solution - Chỉ cảnh báo, không loại bỏ
            if not hasattr(result, 'transmission_solution') or result.transmission_solution is None:
                print(f"DEBUG WARNING: {candidate} - No transmission solution (will be penalized but not rejected)")
                invalid_reasons.append("No transmission solution")
                # Không set is_valid = False, chỉ penalize trong fitness
            
            # Kiểm tra safety_factor - Chỉ loại bỏ nếu quá thấp
            safety_val = getattr(result, 'safety_factor', 0)
            # Ngưỡng an toàn cứng: không bao giờ chấp nhận safety_factor < 4.0
            hard_safety_threshold = 4.0
            sf_threshold = max(hard_safety_threshold, float(self.settings.min_belt_safety_factor))
            if safety_val < sf_threshold:
                print(f"DEBUG INVALID: {candidate} - Safety factor {safety_val} < {sf_threshold} (below hard threshold {hard_safety_threshold})")
                is_valid = False
                invalid_reasons.append(f"Safety factor too low: {safety_val} < {sf_threshold} (hard threshold: {hard_safety_threshold})")
            
            # Kiểm tra budget - Chỉ loại bỏ nếu vượt quá nhiều
            if self.settings.max_budget_usd:
                cost_val = getattr(result, 'cost_capital_total', float('inf'))
                if cost_val > self.settings.max_budget_usd * 1.5:  # Cho phép vượt 50%
                    print(f"DEBUG INVALID: {candidate} - Cost {cost_val} > {self.settings.max_budget_usd * 1.5}")
                    is_valid = False
                    invalid_reasons.append(f"Cost too high: {cost_val}")
            
            # Kiểm tra sai số vận tốc - Cải tiến mới
            if hasattr(result, 'transmission_solution') and result.transmission_solution:
                vel_err = getattr(result.transmission_solution, "velocity_error_percent", 0.0)
                if vel_err > self.settings.max_velocity_error_percent:
                    print(f"DEBUG INVALID: {candidate} - Velocity error {vel_err:.2f}% > {self.settings.max_velocity_error_percent}% (above threshold)")
                    is_valid = False
                    invalid_reasons.append(f"Velocity error too high: {vel_err:.2f}% > {self.settings.max_velocity_error_percent}%")
                elif vel_err > 5.0:  # Cảnh báo nếu > 5% (ngưỡng cảnh báo cố định)
                    print(f"DEBUG WARNING: {candidate} - Velocity error {vel_err:.2f}% above warning threshold 5%")
                    invalid_reasons.append(f"Warning: High velocity error: {vel_err:.2f}%")
                
                # Log sai số vận tốc để theo dõi
                print(f"DEBUG: {candidate} - Velocity error: {vel_err:.2f}%")
            
            # Kiểm tra các cảnh báo quan trọng - Chỉ cảnh báo
            if hasattr(result, 'warnings') and result.warnings:
                for warning in result.warnings:
                    if "vượt năng lực tiết diện" in warning or "bị khống chế bởi tiết diện" in warning:
                        print(f"DEBUG WARNING: {candidate} - Warning: {warning} (will be penalized)")
                        invalid_reasons.append(f"Warning: {warning}")
                        # Không set is_valid = False, chỉ penalize
            
            # Gom speed_warnings vào invalid_reasons để bị phạt trong fitness
            if getattr(candidate, "speed_warnings", None):
                for w in candidate.speed_warnings:
                    invalid_reasons.append(f"Warning: {w}")
            
            # Lưu lý do không hợp lệ để debug
            if invalid_reasons:
                candidate.invalid_reasons = invalid_reasons
            
            candidate.is_valid = is_valid
            print(f"DEBUG: Candidate {candidate} - Valid: {is_valid}, Reasons: {invalid_reasons if invalid_reasons else 'None'}")

        except Exception as e:
            # Nếu có lỗi trong quá trình tính toán, coi như không hợp lệ
            print(f"DEBUG ERROR: Calculation failed for {candidate}: {e}")
            candidate.is_valid = False
            candidate.calculation_result = CalculationResult()
            candidate.calculation_result.warnings.append(f"Lỗi tính toán: {e}")
            candidate.invalid_reasons = [f"Lỗi tính toán: {e}"]

    def _create_safe_candidate(self, belt_width_mm: int = None, belt_type_name: str = None, 
                              gearbox_ratio: float = None, chain_spec_designation: str = None) -> DesignCandidate:
        """Tạo một candidate an toàn với validation và fallback."""
        try:
            # Validation và fallback cho từng gene
            if belt_width_mm is None or belt_width_mm not in STANDARD_WIDTHS:
                belt_width_mm = random.choice(STANDARD_WIDTHS)
                print(f"DEBUG: Invalid belt_width_mm, using fallback: {belt_width_mm}mm")
            
            if belt_type_name is None or belt_type_name not in ACTIVE_BELT_SPECS:
                belt_type_name = random.choice(list(ACTIVE_BELT_SPECS.keys()))
                print(f"DEBUG: Invalid belt_type_name, using fallback: {belt_type_name}")
            
            if gearbox_ratio is None or gearbox_ratio not in STANDARD_GEARBOX_RATIOS:
                gearbox_ratio = random.choice(STANDARD_GEARBOX_RATIOS)
                print(f"DEBUG: Invalid gearbox_ratio, using fallback: {gearbox_ratio}")
            
            if chain_spec_designation is None:
                chain_designations = [cs.designation for cs in ACTIVE_CHAIN_SPECS if cs.designation]
                if chain_designations:
                    chain_spec_designation = random.choice(chain_designations)
                else:
                    chain_spec_designation = "05B"  # Default fallback
                print(f"DEBUG: Invalid chain_spec_designation, using fallback: {chain_spec_designation}")
            
            # Tạo candidate với các gene đã được validate
            candidate = DesignCandidate(
                belt_width_mm=belt_width_mm,
                belt_type_name=belt_type_name,
                gearbox_ratio=gearbox_ratio,
                chain_spec_designation=chain_spec_designation
            )
            
            # Reset state
            candidate.invalid_reasons = []
            
            return candidate
            
        except Exception as e:
            print(f"DEBUG: Error creating safe candidate: {e}, using hardcoded fallback")
            # Hardcoded fallback cuối cùng
            return DesignCandidate(
                belt_width_mm=600,
                belt_type_name="Vải EP (Polyester)",
                gearbox_ratio=20.0,
                chain_spec_designation="05B"
            )

    def _tournament_selection(self, tournament_size: int, population: List[DesignCandidate]) -> DesignCandidate:
        """Lựa chọn cha mẹ bằng phương pháp Tournament Selection với cải tiến."""
        if not population:
            # Fallback: trả về một cá thể ngẫu nhiên từ quần thể gốc nếu không có cá thể hợp lệ
            if self.population:
                return random.choice(self.population)
            else:
                # Tạo một candidate mặc định nếu không có gì
                return DesignCandidate(
                    belt_width_mm=600,
                    belt_type_name="Vải EP (Polyester)",
                    gearbox_ratio=20.0,
                    chain_spec_designation=""
                )
        
        # Cải tiến: Tournament selection với diversity preservation
        tournament = random.sample(population, min(tournament_size, len(population)))
        
        # Sắp xếp theo fitness score (fitness càng thấp càng tốt)
        tournament.sort(key=lambda c: c.fitness_score)
        
        # Cải tiến: Thêm diversity preservation
        # 80% khả năng chọn best, 20% khả năng chọn random để duy trì đa dạng
        if random.random() < 0.8:
            selected = tournament[0]  # Chọn best
            print(f"DEBUG: Tournament selection: Best candidate selected (fitness: {selected.fitness_score:.3f})")
        else:
            # Chọn random từ tournament để duy trì đa dạng
            selected = random.choice(tournament)
            print(f"DEBUG: Tournament selection: Random candidate selected (fitness: {selected.fitness_score:.3f}) for diversity")
        
        return selected

    def _crossover(self, parent1: DesignCandidate, parent2: DesignCandidate) -> Tuple[DesignCandidate, DesignCandidate]:
        """Thực hiện lai ghép với nhiều phương pháp khác nhau."""
        # Sử dụng dataclass fields trực tiếp thay vì __dict__.copy() để an toàn hơn
        genes = ['belt_width_mm', 'belt_type_name', 'gearbox_ratio', 'chain_spec_designation']
        
        # Chọn phương pháp crossover ngẫu nhiên để tăng đa dạng
        crossover_method = random.choice(['single_point', 'two_point', 'uniform'])
        
        if crossover_method == 'single_point':
            # Single-point crossover (đã có)
            crossover_point = random.randint(1, len(genes) - 1)
            
            # Tạo child1
            child1_genes = {}
            for i, gene_name in enumerate(genes):
                if i < crossover_point:
                    child1_genes[gene_name] = getattr(parent1, gene_name)
                else:
                    child1_genes[gene_name] = getattr(parent2, gene_name)
            
            # Tạo child2
            child2_genes = {}
            for i, gene_name in enumerate(genes):
                if i < crossover_point:
                    child2_genes[gene_name] = getattr(parent2, gene_name)
                else:
                    child2_genes[gene_name] = getattr(parent1, gene_name)
                    
        elif crossover_method == 'two_point':
            # Two-point crossover
            if len(genes) >= 3:
                point1 = random.randint(1, len(genes) - 2)
                point2 = random.randint(point1 + 1, len(genes) - 1)
            else:
                point1, point2 = 1, len(genes) - 1
            
            # Tạo child1
            child1_genes = {}
            for i, gene_name in enumerate(genes):
                if i < point1 or i >= point2:
                    child1_genes[gene_name] = getattr(parent1, gene_name)
                else:
                    child1_genes[gene_name] = getattr(parent2, gene_name)
            
            # Tạo child2
            child2_genes = {}
            for i, gene_name in enumerate(genes):
                if i < point1 or i >= point2:
                    child2_genes[gene_name] = getattr(parent2, gene_name)
                else:
                    child2_genes[gene_name] = getattr(parent1, gene_name)
                    
        else:  # uniform crossover
            # Uniform crossover - mỗi gene có 50% khả năng được chọn từ mỗi parent
            child1_genes = {}
            child2_genes = {}
            for gene_name in genes:
                if random.random() < 0.5:
                    child1_genes[gene_name] = getattr(parent1, gene_name)
                    child2_genes[gene_name] = getattr(parent2, gene_name)
                else:
                    child1_genes[gene_name] = getattr(parent2, gene_name)
                    child2_genes[gene_name] = getattr(parent1, gene_name)

        # Tạo cá thể con mới, reset kết quả tính toán
        try:
            child1 = DesignCandidate(**child1_genes)
            child2 = DesignCandidate(**child2_genes)
            
            # Reset các thuộc tính để được đánh giá lại
            child1.invalid_reasons = []
            child2.invalid_reasons = []
            
            # Log crossover method để debug
            print(f"DEBUG: Crossover method: {crossover_method} for parents {parent1.belt_width_mm}mm and {parent2.belt_width_mm}mm")
            
        except Exception as e:
            print(f"Optimizer: Error in crossover: {e}")
            # Fallback: sử dụng hàm helper để tạo candidate an toàn
            child1 = self._create_safe_candidate()
            child2 = self._create_safe_candidate()
        
        return child1, child2

    def _mutate(self, candidate: DesignCandidate, mutation_rate: float):
        """Thực hiện đột biến gen với một xác suất nhất định và cải tiến."""
        belt_types = list(ACTIVE_BELT_SPECS.keys())
        chain_designations = [cs.designation for cs in ACTIVE_CHAIN_SPECS if cs.designation]

        if not chain_designations:
            chain_designations = ["05B", "08A", "16B"]  # Default fallback

        # Cải tiến: Gene-specific mutation rates để tối ưu hóa từng loại gene
        gene_mutation_rates = {
            'belt_width_mm': mutation_rate * 1.2,      # Bề rộng băng - mutation cao hơn để tìm kích thước tối ưu
            'belt_type_name': mutation_rate * 0.8,     # Loại băng - mutation thấp hơn để ổn định
            'gearbox_ratio': mutation_rate * 1.0,      # Tỷ số hộp số - mutation bình thường
            'chain_spec_designation': mutation_rate * 0.9  # Xích - mutation thấp hơn một chút
        }
        
        # Cải tiến: Adaptive mutation dựa trên fitness score
        if hasattr(candidate, 'fitness_score') and candidate.fitness_score != float('inf'):
            # Nếu fitness score cao (kém), tăng mutation rate
            if candidate.fitness_score > 5.0:  # Fitness càng thấp càng tốt
                adaptive_factor = 1.5
                print(f"DEBUG: High fitness score detected ({candidate.fitness_score:.3f}), increasing mutation rate by {adaptive_factor}x")
            else:
                adaptive_factor = 1.0
        else:
            adaptive_factor = 1.0
        
        # Thực hiện mutation với gene-specific rates và adaptive factor
        mutations_applied = []
        
        # Mutation cho bề rộng băng
        if random.random() < gene_mutation_rates['belt_width_mm'] * adaptive_factor:
            old_width = candidate.belt_width_mm
            candidate.belt_width_mm = random.choice(STANDARD_WIDTHS)
            mutations_applied.append(f"belt_width: {old_width}mm -> {candidate.belt_width_mm}mm")
        
        # Mutation cho loại băng
        if random.random() < gene_mutation_rates['belt_type_name'] * adaptive_factor:
            old_type = candidate.belt_type_name
            candidate.belt_type_name = random.choice(belt_types)
            mutations_applied.append(f"belt_type: {old_type} -> {candidate.belt_type_name}")
        
        # Mutation cho tỷ số hộp số
        if random.random() < gene_mutation_rates['gearbox_ratio'] * adaptive_factor:
            old_ratio = candidate.gearbox_ratio
            candidate.gearbox_ratio = random.choice(STANDARD_GEARBOX_RATIOS)
            mutations_applied.append(f"gearbox_ratio: {old_ratio} -> {candidate.gearbox_ratio}")
        
        # Mutation cho xích
        if random.random() < gene_mutation_rates['chain_spec_designation'] * adaptive_factor:
            if chain_designations:
                old_chain = candidate.chain_spec_designation
                candidate.chain_spec_designation = random.choice(chain_designations)
                mutations_applied.append(f"chain: {old_chain} -> {candidate.chain_spec_designation}")
        
        # Log mutations để debug
        if mutations_applied:
            print(f"DEBUG: Mutations applied to candidate {candidate.belt_width_mm}mm: {', '.join(mutations_applied)}")
        
        # Sau khi đột biến, reset kết quả để được đánh giá lại
        candidate.calculation_result = None
        candidate.fitness_score = float('inf')
        candidate.is_valid = False
        candidate.invalid_reasons = []  # Reset invalid reasons
