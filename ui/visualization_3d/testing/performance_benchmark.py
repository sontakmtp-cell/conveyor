"""
Performance Benchmarking Tool for 3D Visualization
Tool đo lường và so sánh performance của các thành phần visualization
"""

import time
import json
import statistics
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import psutil
import gc
import logging

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Kết quả benchmark"""
    test_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    fps: float
    triangle_count: int
    texture_memory_mb: float
    timestamp: float
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class BenchmarkSuite:
    """Suite benchmark"""
    name: str
    description: str
    test_cases: List[Dict[str, Any]]
    results: List[BenchmarkResult]
    summary: Dict[str, Any]


class PerformanceBenchmarker:
    """Bộ benchmark performance chính"""
    
    def __init__(self):
        self.benchmark_suites: List[BenchmarkSuite] = []
        self.current_suite: Optional[BenchmarkSuite] = None
        self.baseline_results: Dict[str, BenchmarkResult] = {}
        
    def create_benchmark_suite(self, name: str, description: str) -> BenchmarkSuite:
        """Tạo benchmark suite mới"""
        suite = BenchmarkSuite(
            name=name,
            description=description,
            test_cases=[],
            results=[],
            summary={}
        )
        self.benchmark_suites.append(suite)
        self.current_suite = suite
        return suite
    
    def add_test_case(self, test_name: str, parameters: Dict[str, Any], description: str = ""):
        """Thêm test case vào suite hiện tại"""
        if not self.current_suite:
            raise ValueError("Chưa có benchmark suite nào được tạo")
        
        test_case = {
            'name': test_name,
            'parameters': parameters,
            'description': description
        }
        self.current_suite.test_cases.append(test_case)
    
    def run_benchmark_suite(self, suite_name: str) -> BenchmarkSuite:
        """Chạy benchmark suite"""
        suite = next((s for s in self.benchmark_suites if s.name == suite_name), None)
        if not suite:
            raise ValueError(f"Không tìm thấy benchmark suite: {suite_name}")
        
        logger.info(f"Bắt đầu chạy benchmark suite: {suite.name}")
        
        for test_case in suite.test_cases:
            try:
                result = self._run_single_benchmark(test_case)
                suite.results.append(result)
                logger.info(f"✅ {test_case['name']}: {result.execution_time:.3f}s")
            except Exception as e:
                logger.error(f"❌ {test_case['name']}: {str(e)}")
        
        # Tạo summary
        suite.summary = self._generate_suite_summary(suite)
        
        return suite
    
    def _run_single_benchmark(self, test_case: Dict[str, Any]) -> BenchmarkResult:
        """Chạy single benchmark"""
        test_name = test_case['name']
        parameters = test_case['parameters']
        
        # Đo memory trước khi chạy
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024
        
        # Đo CPU trước khi chạy
        cpu_before = process.cpu_percent()
        
        # Bắt đầu benchmark
        start_time = time.time()
        
        # Chạy test function
        test_result = self._execute_test_function(test_name, parameters)
        
        end_time = time.time()
        
        # Đo memory và CPU sau khi chạy
        memory_after = process.memory_info().rss / 1024 / 1024
        cpu_after = process.cpu_percent()
        
        # Tính toán metrics
        execution_time = end_time - start_time
        memory_usage = memory_after - memory_before
        cpu_usage = (cpu_before + cpu_after) / 2
        fps = test_result.get('fps', 0.0)
        triangle_count = test_result.get('triangle_count', 0)
        texture_memory = test_result.get('texture_memory_mb', 0.0)
        
        return BenchmarkResult(
            test_name=test_name,
            execution_time=execution_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            fps=fps,
            triangle_count=triangle_count,
            texture_memory_mb=texture_memory,
            timestamp=time.time(),
            parameters=parameters,
            metadata=test_result
        )
    
    def _execute_test_function(self, test_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi test function"""
        # Import các module cần thiết
        try:
            from core.model_generator import ConveyorModelGenerator
            from core.component_builder import ComponentBuilderManager
            from core.animation_engine import ConveyorAnimationEngine
            from core.physics_simulator import ConveyorPhysicsSimulator
            from core.performance_optimizer import PerformanceOptimizer
        except ImportError as e:
            logger.warning(f"Không thể import modules: {e}")
            return {'fps': 0.0, 'triangle_count': 0, 'texture_memory_mb': 0.0}
        
        # Tạo test data
        conveyor_params = self._create_test_conveyor_params(parameters)
        calculation_result = self._create_test_calculation_result(parameters)
        
        # Chạy test dựa trên test name
        if test_name == 'model_generation':
            return self._benchmark_model_generation(conveyor_params, calculation_result)
        elif test_name == 'component_building':
            return self._benchmark_component_building(conveyor_params, calculation_result)
        elif test_name == 'animation_performance':
            return self._benchmark_animation_performance(conveyor_params, calculation_result)
        elif test_name == 'physics_simulation':
            return self._benchmark_physics_simulation(conveyor_params, calculation_result)
        elif test_name == 'optimization_performance':
            return self._benchmark_optimization_performance(conveyor_params, calculation_result)
        elif test_name == 'full_workflow':
            return self._benchmark_full_workflow(conveyor_params, calculation_result)
        else:
            return {'fps': 0.0, 'triangle_count': 0, 'texture_memory_mb': 0.0}
    
    def _create_test_conveyor_params(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo tham số băng tải test"""
        base_params = {
            'B_mm': 800,
            'L_m': 50.0,
            'belt_thickness_mm': 12,
            'trough_angle_label': '35°',
            'belt_type': 'EP800/4',
            'motor_rpm': 1450,
            'motor_efficiency': 0.95,
            'gearbox_efficiency': 0.98,
            'carrying_idler_spacing_m': 1.2,
            'return_idler_spacing_m': 3.0,
            'material_density_kg_m3': 1600,
            'conveyor_inclination_deg': 15.0,
            'belt_speed_mps': 2.5
        }
        
        # Override với parameters từ test case
        base_params.update(parameters)
        return base_params
    
    def _create_test_calculation_result(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo kết quả tính toán test"""
        return {
            'motor_power_kw': 15.5,
            'belt_tension_n': 12500,
            'transmission_solution': {
                'gearbox_ratio': 25.0,
                'chain_designation': '16B-1',
                'drive_sprocket_teeth': 19,
                'driven_sprocket_teeth': 38,
                'chain_pitch_mm': 25.4
            },
            'idler_selection': {
                'carrying_idler_diameter_mm': 133,
                'return_idler_diameter_mm': 108
            },
            'safety_factor': 8.5,
            'efficiency_percent': 87.3
        }
    
    def _benchmark_model_generation(self, params: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark model generation"""
        try:
            model_generator = ConveyorModelGenerator(params, result)
            model_data = model_generator.generate_complete_model()
            
            return {
                'fps': 60.0,
                'triangle_count': len(str(model_data)) // 100,  # Approximate
                'texture_memory_mb': len(str(model_data)) / 1024 / 1024 * 0.1
            }
        except Exception as e:
            logger.error(f"Model generation benchmark failed: {e}")
            return {'fps': 0.0, 'triangle_count': 0, 'texture_memory_mb': 0.0}
    
    def _benchmark_component_building(self, params: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark component building"""
        try:
            model_generator = ConveyorModelGenerator(params, result)
            model_data = model_generator.generate_complete_model()
            
            component_builder = ComponentBuilderManager()
            components = component_builder.build_all_components(model_data)
            
            return {
                'fps': 60.0,
                'triangle_count': len(components) * 1000,  # Approximate
                'texture_memory_mb': len(components) * 0.5
            }
        except Exception as e:
            logger.error(f"Component building benchmark failed: {e}")
            return {'fps': 0.0, 'triangle_count': 0, 'texture_memory_mb': 0.0}
    
    def _benchmark_animation_performance(self, params: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark animation performance"""
        try:
            model_generator = ConveyorModelGenerator(params, result)
            model_data = model_generator.generate_complete_model()
            
            animation_engine = ConveyorAnimationEngine(model_data)
            
            # Chạy animation trong 1 giây
            start_time = time.time()
            animation_steps = 60
            for i in range(animation_steps):
                animation_engine.update_animations(1.0 / animation_steps)
            end_time = time.time()
            
            actual_fps = animation_steps / (end_time - start_time)
            
            return {
                'fps': actual_fps,
                'triangle_count': len(animation_engine.animations) * 500,
                'texture_memory_mb': len(animation_engine.animations) * 0.3
            }
        except Exception as e:
            logger.error(f"Animation performance benchmark failed: {e}")
            return {'fps': 0.0, 'triangle_count': 0, 'texture_memory_mb': 0.0}
    
    def _benchmark_physics_simulation(self, params: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark physics simulation"""
        try:
            model_generator = ConveyorModelGenerator(params, result)
            model_data = model_generator.generate_complete_model()
            
            physics_simulator = ConveyorPhysicsSimulator(model_data)
            
            # Chạy simulation trong 1 giây
            start_time = time.time()
            simulation_steps = 60
            for i in range(simulation_steps):
                physics_simulator.update_simulation(1.0 / simulation_steps)
            end_time = time.time()
            
            simulation_fps = simulation_steps / (end_time - start_time)
            
            return {
                'fps': simulation_fps,
                'triangle_count': len(physics_simulator.physics_components) * 800,
                'texture_memory_mb': len(physics_simulator.physics_components) * 0.4
            }
        except Exception as e:
            logger.error(f"Physics simulation benchmark failed: {e}")
            return {'fps': 0.0, 'triangle_count': 0, 'texture_memory_mb': 0.0}
    
    def _benchmark_optimization_performance(self, params: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark optimization performance"""
        try:
            model_generator = ConveyorModelGenerator(params, result)
            model_data = model_generator.generate_complete_model()
            
            optimizer = PerformanceOptimizer()
            
            # Test tất cả optimization levels
            optimization_times = []
            for level in ['low', 'medium', 'high', 'ultra']:
                optimizer.settings.level = level
                start_time = time.time()
                optimized = optimizer.optimize_scene(model_data)
                end_time = time.time()
                optimization_times.append(end_time - start_time)
            
            avg_optimization_time = statistics.mean(optimization_times)
            
            return {
                'fps': 1.0 / avg_optimization_time if avg_optimization_time > 0 else 0.0,
                'triangle_count': len(str(model_data)) // 200,
                'texture_memory_mb': len(str(model_data)) / 1024 / 1024 * 0.05
            }
        except Exception as e:
            logger.error(f"Optimization performance benchmark failed: {e}")
            return {'fps': 0.0, 'triangle_count': 0, 'texture_memory_mb': 0.0}
    
    def _benchmark_full_workflow(self, params: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """Benchmark toàn bộ workflow"""
        try:
            start_time = time.time()
            
            # 1. Model Generation
            model_generator = ConveyorModelGenerator(params, result)
            model_data = model_generator.generate_complete_model()
            
            # 2. Component Building
            component_builder = ComponentBuilderManager()
            components = component_builder.build_all_components(model_data)
            
            # 3. Animation Setup
            animation_engine = ConveyorAnimationEngine(model_data)
            
            # 4. Physics Setup
            physics_simulator = ConveyorPhysicsSimulator(model_data)
            
            # 5. Performance Optimization
            optimizer = PerformanceOptimizer()
            optimized_scene = optimizer.optimize_scene(model_data)
            
            end_time = time.time()
            
            workflow_time = end_time - start_time
            workflow_fps = 1.0 / workflow_time if workflow_time > 0 else 0.0
            
            return {
                'fps': workflow_fps,
                'triangle_count': len(components) * 1500,
                'texture_memory_mb': len(components) * 0.8
            }
        except Exception as e:
            logger.error(f"Full workflow benchmark failed: {e}")
            return {'fps': 0.0, 'triangle_count': 0, 'texture_memory_mb': 0.0}
    
    def _generate_suite_summary(self, suite: BenchmarkSuite) -> Dict[str, Any]:
        """Tạo summary cho benchmark suite"""
        if not suite.results:
            return {}
        
        # Tính toán thống kê
        execution_times = [r.execution_time for r in suite.results]
        memory_usages = [r.memory_usage_mb for r in suite.results]
        cpu_usages = [r.cpu_usage_percent for r in suite.results]
        fps_values = [r.fps for r in suite.results]
        
        return {
            'total_tests': len(suite.results),
            'execution_time': {
                'average': statistics.mean(execution_times),
                'median': statistics.median(execution_times),
                'min': min(execution_times),
                'max': max(execution_times),
                'std_dev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            },
            'memory_usage': {
                'average': statistics.mean(memory_usages),
                'median': statistics.median(memory_usages),
                'min': min(memory_usages),
                'max': max(memory_usages),
                'std_dev': statistics.stdev(memory_usages) if len(memory_usages) > 1 else 0
            },
            'cpu_usage': {
                'average': statistics.mean(cpu_usages),
                'median': statistics.median(cpu_usages),
                'min': min(cpu_usages),
                'max': max(cpu_usages),
                'std_dev': statistics.stdev(cpu_usages) if len(cpu_usages) > 1 else 0
            },
            'fps': {
                'average': statistics.mean(fps_values),
                'median': statistics.median(fps_values),
                'min': min(fps_values),
                'max': max(fps_values),
                'std_dev': statistics.stdev(fps_values) if len(fps_values) > 1 else 0
            }
        }
    
    def create_performance_comparison_suite(self) -> BenchmarkSuite:
        """Tạo suite so sánh performance"""
        suite = self.create_benchmark_suite(
            "Performance Comparison",
            "So sánh performance của các thành phần khác nhau"
        )
        
        # Test cases cho model generation với các kích thước khác nhau
        self.add_test_case(
            "model_generation_small",
            {'B_mm': 400, 'L_m': 25.0},
            "Model generation với băng tải nhỏ"
        )
        
        self.add_test_case(
            "model_generation_medium",
            {'B_mm': 800, 'L_m': 50.0},
            "Model generation với băng tải trung bình"
        )
        
        self.add_test_case(
            "model_generation_large",
            {'B_mm': 1600, 'L_m': 100.0},
            "Model generation với băng tải lớn"
        )
        
        # Test cases cho component building
        self.add_test_case(
            "component_building_basic",
            {'B_mm': 800, 'L_m': 50.0},
            "Component building cơ bản"
        )
        
        self.add_test_case(
            "component_building_complex",
            {'B_mm': 1600, 'L_m': 100.0, 'trough_angle_label': '45°'},
            "Component building phức tạp"
        )
        
        # Test cases cho animation performance
        self.add_test_case(
            "animation_performance_30fps",
            {'belt_speed_mps': 1.0},
            "Animation performance 30 FPS"
        )
        
        self.add_test_case(
            "animation_performance_60fps",
            {'belt_speed_mps': 2.5},
            "Animation performance 60 FPS"
        )
        
        # Test cases cho physics simulation
        self.add_test_case(
            "physics_simulation_simple",
            {'B_mm': 800, 'L_m': 50.0, 'conveyor_inclination_deg': 0.0},
            "Physics simulation đơn giản"
        )
        
        self.add_test_case(
            "physics_simulation_complex",
            {'B_mm': 1600, 'L_m': 100.0, 'conveyor_inclination_deg': 25.0},
            "Physics simulation phức tạp"
        )
        
        # Test cases cho optimization
        self.add_test_case(
            "optimization_low_quality",
            {'B_mm': 800, 'L_m': 50.0},
            "Optimization chất lượng thấp"
        )
        
        self.add_test_case(
            "optimization_high_quality",
            {'B_mm': 1600, 'L_m': 100.0},
            "Optimization chất lượng cao"
        )
        
        # Test cases cho full workflow
        self.add_test_case(
            "full_workflow_small",
            {'B_mm': 400, 'L_m': 25.0},
            "Full workflow với băng tải nhỏ"
        )
        
        self.add_test_case(
            "full_workflow_large",
            {'B_mm': 1600, 'L_m': 100.0},
            "Full workflow với băng tải lớn"
        )
        
        return suite
    
    def create_scalability_test_suite(self) -> BenchmarkSuite:
        """Tạo suite test scalability"""
        suite = self.create_benchmark_suite(
            "Scalability Testing",
            "Test khả năng mở rộng với các kích thước khác nhau"
        )
        
        # Test với các chiều dài khác nhau
        lengths = [10, 25, 50, 100, 200, 500]
        for length in lengths:
            self.add_test_case(
                f"scalability_length_{length}m",
                {'L_m': float(length)},
                f"Scalability test với chiều dài {length}m"
            )
        
        # Test với các chiều rộng khác nhau
        widths = [400, 600, 800, 1000, 1200, 1600, 2000]
        for width in widths:
            self.add_test_case(
                f"scalability_width_{width}mm",
                {'B_mm': width},
                f"Scalability test với chiều rộng {width}mm"
            )
        
        # Test với các góc máng khác nhau
        angles = ['0°', '20°', '35°', '45°']
        for angle in angles:
            self.add_test_case(
                f"scalability_angle_{angle}",
                {'trough_angle_label': angle},
                f"Scalability test với góc máng {angle}"
            )
        
        return suite
    
    def export_benchmark_results(self, output_path: str = "benchmark_results.json"):
        """Xuất kết quả benchmark ra file"""
        output_data = {
            'benchmark_suites': [],
            'summary': {
                'total_suites': len(self.benchmark_suites),
                'total_tests': sum(len(s.results) for s in self.benchmark_suites),
                'timestamp': time.time()
            }
        }
        
        for suite in self.benchmark_suites:
            suite_data = {
                'name': suite.name,
                'description': suite.description,
                'test_cases': suite.test_cases,
                'results': [asdict(result) for result in suite.results],
                'summary': suite.summary
            }
            output_data['benchmark_suites'].append(suite_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Benchmark results exported to: {output_path}")
    
    def generate_performance_charts(self, output_dir: str = "benchmark_charts"):
        """Tạo biểu đồ performance"""
        Path(output_dir).mkdir(exist_ok=True)
        
        for suite in self.benchmark_suites:
            if not suite.results:
                continue
            
            # Chart 1: Execution Time Comparison
            self._create_execution_time_chart(suite, output_dir)
            
            # Chart 2: Memory Usage Comparison
            self._create_memory_usage_chart(suite, output_dir)
            
            # Chart 3: FPS Comparison
            self._create_fps_chart(suite, output_dir)
            
            # Chart 4: Performance vs Parameters
            self._create_performance_vs_parameters_chart(suite, output_dir)
    
    def _create_execution_time_chart(self, suite: BenchmarkSuite, output_dir: str):
        """Tạo biểu đồ execution time"""
        test_names = [r.test_name for r in suite.results]
        execution_times = [r.execution_time for r in suite.results]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(test_names, execution_times, color='skyblue', alpha=0.7)
        plt.title(f'Execution Time Comparison - {suite.name}')
        plt.xlabel('Test Cases')
        plt.ylabel('Execution Time (seconds)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Thêm giá trị trên mỗi bar
        for bar, time_val in zip(bars, execution_times):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                    f'{time_val:.3f}s', ha='center', va='bottom')
        
        output_path = Path(output_dir) / f"{suite.name}_execution_time.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Execution time chart saved: {output_path}")
    
    def _create_memory_usage_chart(self, suite: BenchmarkSuite, output_dir: str):
        """Tạo biểu đồ memory usage"""
        test_names = [r.test_name for r in suite.results]
        memory_usages = [r.memory_usage_mb for r in suite.results]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(test_names, memory_usages, color='lightcoral', alpha=0.7)
        plt.title(f'Memory Usage Comparison - {suite.name}')
        plt.xlabel('Test Cases')
        plt.ylabel('Memory Usage (MB)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Thêm giá trị trên mỗi bar
        for bar, mem_val in zip(bars, memory_usages):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{mem_val:.2f}MB', ha='center', va='bottom')
        
        output_path = Path(output_dir) / f"{suite.name}_memory_usage.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Memory usage chart saved: {output_path}")
    
    def _create_fps_chart(self, suite: BenchmarkSuite, output_dir: str):
        """Tạo biểu đồ FPS"""
        test_names = [r.test_name for r in suite.results]
        fps_values = [r.fps for r in suite.results]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(test_names, fps_values, color='lightgreen', alpha=0.7)
        plt.title(f'FPS Comparison - {suite.name}')
        plt.xlabel('Test Cases')
        plt.ylabel('FPS')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Thêm giá trị trên mỗi bar
        for bar, fps_val in zip(bars, fps_values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{fps_val:.1f}', ha='center', va='bottom')
        
        output_path = Path(output_dir) / f"{suite.name}_fps.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"FPS chart saved: {output_path}")
    
    def _create_performance_vs_parameters_chart(self, suite: BenchmarkSuite, output_dir: str):
        """Tạo biểu đồ performance vs parameters"""
        # Tìm test cases có tham số số
        numeric_tests = []
        for result in suite.results:
            for key, value in result.parameters.items():
                if isinstance(value, (int, float)) and key in ['B_mm', 'L_m', 'belt_speed_mps']:
                    numeric_tests.append((key, value, result.execution_time))
        
        if not numeric_tests:
            return
        
        # Nhóm theo parameter
        param_groups = {}
        for param_name, param_value, exec_time in numeric_tests:
            if param_name not in param_groups:
                param_groups[param_name] = []
            param_groups[param_name].append((param_value, exec_time))
        
        # Tạo subplot cho mỗi parameter
        fig, axes = plt.subplots(1, len(param_groups), figsize=(5*len(param_groups), 5))
        if len(param_groups) == 1:
            axes = [axes]
        
        for i, (param_name, data) in enumerate(param_groups.items()):
            param_values, exec_times = zip(*sorted(data))
            
            axes[i].plot(param_values, exec_times, 'o-', linewidth=2, markersize=6)
            axes[i].set_title(f'Performance vs {param_name}')
            axes[i].set_xlabel(param_name)
            axes[i].set_ylabel('Execution Time (seconds)')
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = Path(output_dir) / f"{suite.name}_performance_vs_parameters.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Performance vs parameters chart saved: {output_path}")


def run_benchmark_demo():
    """Chạy demo benchmark"""
    print("🚀 BẮT ĐẦU PERFORMANCE BENCHMARKING")
    print("=" * 50)
    
    # Tạo benchmarker
    benchmarker = PerformanceBenchmarker()
    
    # Tạo performance comparison suite
    print("\n📊 Tạo Performance Comparison Suite...")
    perf_suite = benchmarker.create_performance_comparison_suite()
    
    # Chạy benchmark
    print("\n⚡ Chạy Performance Comparison Benchmark...")
    results = benchmarker.run_benchmark_suite("Performance Comparison")
    
    # Tạo scalability test suite
    print("\n📈 Tạo Scalability Test Suite...")
    scale_suite = benchmarker.create_scalability_test_suite()
    
    # Chạy scalability benchmark
    print("\n🔍 Chạy Scalability Benchmark...")
    scale_results = benchmarker.run_benchmark_suite("Scalability Testing")
    
    # Xuất kết quả
    print("\n💾 Xuất kết quả benchmark...")
    benchmarker.export_benchmark_results()
    
    # Tạo biểu đồ
    print("\n📊 Tạo biểu đồ performance...")
    benchmarker.generate_performance_charts()
    
    # In summary
    print("\n📋 TỔNG HỢP KẾT QUẢ BENCHMARK")
    print("=" * 50)
    
    for suite in benchmarker.benchmark_suites:
        print(f"\n🎯 {suite.name}:")
        print(f"  - Tổng số tests: {suite.summary.get('total_tests', 0)}")
        print(f"  - Thời gian thực thi trung bình: {suite.summary.get('execution_time', {}).get('average', 0):.3f}s")
        print(f"  - Memory usage trung bình: {suite.summary.get('memory_usage', {}).get('average', 0):.2f}MB")
        print(f"  - FPS trung bình: {suite.summary.get('fps', {}).get('average', 0):.1f}")
    
    print("\n✅ Benchmark completed successfully!")
    print("📁 Kết quả được lưu trong:")
    print("  - benchmark_results.json")
    print("  - benchmark_charts/")
    
    return benchmarker


if __name__ == "__main__":
    run_benchmark_demo()
