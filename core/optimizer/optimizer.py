# core/optimizer/optimizer.py
import random
import copy
import math
import sys # Added for flushing print statements
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
    MATERIAL_DB
)

class Optimizer:
    def __init__(self, base_params: ConveyorParameters, settings: OptimizerSettings):
        self.base_params = base_params
        self.settings = settings
        self.population: List[DesignCandidate] = []

    def run(self, generations: int = 50, population_size: int = 100, mutation_rate: float = 0.1, tournament_size: int = 5, elitism_count: int = 10) -> List[DesignCandidate]:
        """Chạy toàn bộ quá trình tối ưu hóa GA."""
        try:
            self._initialize_population(population_size)
        except Exception as e:
            print(f"Optimizer: Failed to initialize population: {e}")
            return []

        for gen in range(generations):
            print(f"Optimizer: Running Generation {gen + 1}/{generations}")
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

            new_generation = valid_population[:elitism_count] # Giữ lại cá thể tinh hoa

            while len(new_generation) < population_size:
                parent1 = self._tournament_selection(tournament_size, valid_population)
                parent2 = self._tournament_selection(tournament_size, valid_population)
                child1, child2 = self._crossover(parent1, parent2)
                self._mutate(child1, mutation_rate)
                self._mutate(child2, mutation_rate)
                new_generation.extend([child1, child2])
            
            self.population = new_generation

        # Đánh giá lại lần cuối và trả về kết quả tốt nhất
        print("Optimizer: Final evaluation...")
        self._evaluate_population()
        self.population.sort(key=lambda c: c.fitness_score)
        
        valid_results = [c for c in self.population if c.is_valid]
        print(f"Optimizer: Found {len(valid_results)} valid solutions.")
        return valid_results[:10] # Trả về top 10

    def _initialize_population(self, size: int):
        """Tạo quần thể ban đầu một cách ngẫu nhiên."""
        self.population = []
        material_info = MATERIAL_DB.get(self.base_params.material, {})
        v_max = material_info.get('v_max', 3.0)
        
        belt_types = list(ACTIVE_BELT_SPECS.keys())
        chain_designations = [cs.designation for cs in ACTIVE_CHAIN_SPECS if cs.designation]

        if not chain_designations:
            raise ValueError("No chain specifications found. Cannot initialize population.")

        # Tạo một số candidate "an toàn" dựa trên tham số gốc
        safe_candidates = []
        base_width = self.base_params.B_mm
        base_speed = self.base_params.V_mps
        
        # Candidate 1: Giữ nguyên tham số gốc
        if base_width > 0 and base_speed > 0:
            safe_candidates.append(DesignCandidate(
                belt_width_mm=base_width,
                belt_speed_mps=base_speed,
                belt_type_name=self.base_params.belt_type,
                gearbox_ratio=STANDARD_GEARBOX_RATIOS[0] if STANDARD_GEARBOX_RATIOS else 20.0,
                chain_spec_designation=chain_designations[0] if chain_designations else ""
            ))
        
        # Candidate 2: Giảm tốc độ, giữ nguyên bề rộng
        if base_width > 0:
            safe_candidates.append(DesignCandidate(
                belt_width_mm=base_width,
                belt_speed_mps=max(0.5, base_speed * 0.8),
                belt_type_name=self.base_params.belt_type,
                gearbox_ratio=STANDARD_GEARBOX_RATIOS[0] if STANDARD_GEARBOX_RATIOS else 20.0,
                chain_spec_designation=chain_designations[0] if chain_designations else ""
            ))
        
        # Candidate 3: Tăng bề rộng, giữ nguyên tốc độ
        if base_speed > 0:
            wider_widths = [w for w in STANDARD_WIDTHS if w > base_width]
            if wider_widths:
                safe_candidates.append(DesignCandidate(
                    belt_width_mm=wider_widths[0],
                    belt_speed_mps=base_speed,
                    belt_type_name=self.base_params.belt_type,
                    gearbox_ratio=STANDARD_GEARBOX_RATIOS[0] if STANDARD_GEARBOX_RATIOS else 20.0,
                    chain_spec_designation=chain_designations[0] if chain_designations else ""
                ))

        # Thêm các candidate an toàn vào đầu quần thể
        self.population.extend(safe_candidates)
        print(f"Optimizer: Added {len(safe_candidates)} safe candidates based on original parameters")

        # Tạo các candidate ngẫu nhiên cho phần còn lại
        remaining_size = size - len(safe_candidates)
        for _ in range(remaining_size):
            candidate = DesignCandidate(
                belt_width_mm=random.choice(STANDARD_WIDTHS),
                belt_speed_mps=random.uniform(0.5, v_max),
                belt_type_name=random.choice(belt_types),
                gearbox_ratio=random.choice(STANDARD_GEARBOX_RATIOS),
                chain_spec_designation=random.choice(chain_designations)
            )
            self.population.append(candidate)
        
        print(f"Optimizer: Initialized population with {len(self.population)} candidates ({len(safe_candidates)} safe + {remaining_size} random)")

    def _evaluate_population(self):
        """Đánh giá từng cá thể trong quần thể, chuẩn hóa và tính điểm fitness."""
        # Bước 1: Chạy tính toán cho các cá thể chưa được đánh giá
        with ThreadPoolExecutor() as executor:
            list(executor.map(self._evaluate_candidate, [c for c in self.population if c.calculation_result is None]))

        valid_candidates = [c for c in self.population if c.is_valid]
        if not valid_candidates:
            print("Optimizer: No valid candidates found in population. Trying to relax constraints...")
            
            # Thử làm mềm tiêu chí để tìm được ít nhất một số candidate
            relaxed_candidates = []
            for c in self.population:
                if hasattr(c, 'calculation_result') and c.calculation_result:
                    # Chỉ kiểm tra safety factor cực thấp
                    safety_val = getattr(c.calculation_result, 'safety_factor', 0)
                    if safety_val >= 1.0:  # Giảm xuống 1.0
                        c.is_valid = True
                        relaxed_candidates.append(c)
                        print(f"Optimizer: Relaxed candidate {c} with safety factor {safety_val}")
            
            if relaxed_candidates:
                valid_candidates = relaxed_candidates
                print(f"Optimizer: Found {len(valid_candidates)} candidates after relaxing constraints")
            else:
                print("Optimizer: Still no valid candidates even after relaxing constraints. Stopping.")
                return

        # Bước 2: Tìm min/max cho việc chuẩn hóa (với kiểm tra an toàn)
        min_cost = min(getattr(c.calculation_result, 'cost_capital_total', float('inf')) for c in valid_candidates)
        max_cost = max(getattr(c.calculation_result, 'cost_capital_total', 0) for c in valid_candidates)
        min_power = min(getattr(c.calculation_result, 'required_power_kw', float('inf')) for c in valid_candidates)
        max_power = max(getattr(c.calculation_result, 'required_power_kw', 0) for c in valid_candidates)
        min_safety = min(getattr(c.calculation_result, 'safety_factor', float('inf')) for c in valid_candidates)
        max_safety = max(getattr(c.calculation_result, 'safety_factor', 0) for c in valid_candidates)

        # Bước 3: Tính điểm fitness cho từng cá thể hợp lệ
        for c in valid_candidates:
            cost = getattr(c.calculation_result, 'cost_capital_total', 0)
            power = getattr(c.calculation_result, 'required_power_kw', 0)
            safety = getattr(c.calculation_result, 'safety_factor', 0)

            cost_norm = (cost - min_cost) / (max_cost - min_cost) if max_cost > min_cost else 0
            power_norm = (power - min_power) / (max_power - min_power) if max_power > min_power else 0
            safety_norm = (safety - min_safety) / (max_safety - min_safety) if max_safety > min_safety else 1

            # Tính fitness cơ bản
            base_fitness = (
                self.settings.w_cost * cost_norm
                + self.settings.w_power * power_norm
                - self.settings.w_safety * safety_norm
            )
            
            # Penalize các vấn đề (nhưng không loại bỏ hoàn toàn)
            penalty = 0.0
            if hasattr(c, 'invalid_reasons'):
                for reason in c.invalid_reasons:
                    if "No transmission solution" in reason:
                        penalty += 0.3  # Penalty 30% cho không có transmission
                    elif "Warning:" in reason:
                        penalty += 0.2  # Penalty 20% cho warnings
                    elif "Cost too high" in reason:
                        penalty += 0.1  # Penalty 10% cho cost cao
            
            c.fitness_score = base_fitness + penalty

    def _evaluate_candidate(self, candidate: DesignCandidate):
        """Chạy core.engine.calculate và kiểm tra tính hợp lệ cho một cá thể."""
        params = copy.deepcopy(self.base_params)
        params.B_mm = candidate.belt_width_mm
        params.V_mps = candidate.belt_speed_mps
        params.belt_type = candidate.belt_type_name
        # Chế độ manual để sử dụng gearbox_ratio của candidate
        params.gearbox_ratio_mode = "manual"
        params.gearbox_ratio_user = candidate.gearbox_ratio

        try:
            print(f"DEBUG: Evaluating candidate {candidate}")
            result = calculate(params)
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
            if safety_val < 3.0:  # Giảm từ 8.0 xuống 3.0
                print(f"DEBUG INVALID: {candidate} - Safety factor {safety_val} < 3.0 (too low)")
                is_valid = False
                invalid_reasons.append(f"Safety factor too low: {safety_val}")
            
            # Kiểm tra budget - Chỉ loại bỏ nếu vượt quá nhiều
            if self.settings.max_budget_usd:
                cost_val = getattr(result, 'cost_capital_total', float('inf'))
                if cost_val > self.settings.max_budget_usd * 1.5:  # Cho phép vượt 50%
                    print(f"DEBUG INVALID: {candidate} - Cost {cost_val} > {self.settings.max_budget_usd * 1.5}")
                    is_valid = False
                    invalid_reasons.append(f"Cost too high: {cost_val}")
            
            # Kiểm tra các cảnh báo quan trọng - Chỉ cảnh báo
            if hasattr(result, 'warnings') and result.warnings:
                for warning in result.warnings:
                    if "vượt năng lực tiết diện" in warning or "bị khống chế bởi tiết diện" in warning:
                        print(f"DEBUG WARNING: {candidate} - Warning: {warning} (will be penalized)")
                        invalid_reasons.append(f"Warning: {warning}")
                        # Không set is_valid = False, chỉ penalize
            
            # Lưu lý do không hợp lệ để debug
            if invalid_reasons:
                candidate.invalid_reasons = invalid_reasons
            
            candidate.is_valid = is_valid
            print(f"DEBUG: Candidate {candidate} - Valid: {is_valid}, Reasons: {invalid_reasons if invalid_reasons else 'None'}")

        except Exception as e:
            # Nếu có lỗi trong quá trình tính toán, coi như không hợp lệ
            candidate.is_valid = False
            candidate.calculation_result = CalculationResult()
            candidate.calculation_result.warnings.append(f"Lỗi tính toán: {e}")

    def _tournament_selection(self, tournament_size: int, population: List[DesignCandidate]) -> DesignCandidate:
        """Lựa chọn cha mẹ bằng phương pháp Tournament Selection."""
        if not population:
            # Fallback: trả về một cá thể ngẫu nhiên từ quần thể gốc nếu không có cá thể hợp lệ
            return random.choice(self.population)
        
        tournament = random.sample(population, min(tournament_size, len(population)))
        tournament.sort(key=lambda c: c.fitness_score)
        return tournament[0]

    def _crossover(self, parent1: DesignCandidate, parent2: DesignCandidate) -> Tuple[DesignCandidate, DesignCandidate]:
        """Thực hiện lai ghép single-point crossover."""
        child1_data = parent1.__dict__.copy()
        child2_data = parent2.__dict__.copy()

        genes = ['belt_width_mm', 'belt_speed_mps', 'belt_type_name', 'gearbox_ratio', 'chain_spec_designation']
        crossover_point = random.randint(1, len(genes) - 1)
        
        for i in range(crossover_point, len(genes)):
            gene_name = genes[i]
            child1_data[gene_name], child2_data[gene_name] = child2_data[gene_name], child1_data[gene_name]

        # Tạo cá thể con mới, reset kết quả tính toán
        child1 = DesignCandidate(**{k: v for k, v in child1_data.items() if k in genes})
        child2 = DesignCandidate(**{k: v for k, v in child2_data.items() if k in genes})
        
        return child1, child2

    def _mutate(self, candidate: DesignCandidate, mutation_rate: float):
        """Thực hiện đột biến gen với một xác suất nhất định."""
        material_info = MATERIAL_DB.get(self.base_params.material, {})
        v_max = material_info.get('v_max', 3.0)
        belt_types = list(ACTIVE_BELT_SPECS.keys())
        chain_designations = [cs.designation for cs in ACTIVE_CHAIN_SPECS if cs.designation]

        if random.random() < mutation_rate:
            candidate.belt_width_mm = random.choice(STANDARD_WIDTHS)
        if random.random() < mutation_rate:
            candidate.belt_speed_mps = random.uniform(0.5, v_max)
        if random.random() < mutation_rate:
            candidate.belt_type_name = random.choice(belt_types)
        if random.random() < mutation_rate:
            candidate.gearbox_ratio = random.choice(STANDARD_GEARBOX_RATIOS)
        if random.random() < mutation_rate:
            if chain_designations:
                candidate.chain_spec_designation = random.choice(chain_designations)
        
        # Sau khi đột biến, reset kết quả để được đánh giá lại
        candidate.calculation_result = None
        candidate.fitness_score = float('inf')
        candidate.is_valid = False
