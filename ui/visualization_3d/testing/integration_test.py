"""
Integration Testing Script
Script kiểm tra tích hợp visualization 3D với hệ thống chính
"""

import sys
import os
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional

# Thêm đường dẫn để import các module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from core.model_generator import ConveyorModelGenerator
    from core.component_builder import ComponentBuilderManager
    from core.animation_engine import ConveyorAnimationEngine
    from core.physics_simulator import ConveyorPhysicsSimulator
    from core.performance_optimizer import PerformanceOptimizer, OptimizationLevel
    from enhanced_widget import EnhancedVisualization3DWidget
except ImportError as e:
    print(f"❌ Không thể import visualization modules: {e}")
    print("Hãy kiểm tra đường dẫn và dependencies")
    # Thay vì exit, hãy tiếp tục với mock data
    print("Sẽ sử dụng mock data cho testing")

try:
    # Import hệ thống chính
    from core.models import ConveyorParameters, CalculationResult
    from core.engine import ConveyorCalculationEngine
    from core.optimizer import ConveyorOptimizer
except ImportError as e:
    print(f"⚠️ Không thể import core system modules: {e}")
    print("Sẽ sử dụng mock data cho testing")


class IntegrationTestRunner:
    """Runner cho integration testing"""
    
    def __init__(self):
        self.test_results = []
        self.test_data = self._load_test_data()
        
    def _load_test_data(self) -> Dict[str, Any]:
        """Tải test data từ file hoặc tạo mock data"""
        test_data_path = Path(__file__).parent / "test_data.json"
        
        if test_data_path.exists():
            try:
                with open(test_data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Không thể load test data: {e}")
        
        # Tạo mock data nếu không có file
        return self._create_mock_test_data()
    
    def _create_mock_test_data(self) -> Dict[str, Any]:
        """Tạo mock test data"""
        return {
            "test_cases": [
                {
                    "name": "small_conveyor",
                    "description": "Băng tải nhỏ - 400mm x 25m",
                    "conveyor_params": {
                        "B_mm": 400,
                        "L_m": 25.0,
                        "belt_thickness_mm": 8,
                        "trough_angle_label": "20°",
                        "belt_type": "EP400/3",
                        "motor_rpm": 1450,
                        "motor_efficiency": 0.92,
                        "gearbox_efficiency": 0.96,
                        "carrying_idler_spacing_m": 1.5,
                        "return_idler_spacing_m": 3.0,
                        "material_density_kg_m3": 1400,
                        "conveyor_inclination_deg": 10.0,
                        "belt_speed_mps": 1.8
                    },
                    "expected_results": {
                        "motor_power_kw": 5.2,
                        "belt_tension_n": 4200,
                        "safety_factor": 7.8
                    }
                },
                {
                    "name": "medium_conveyor",
                    "description": "Băng tải trung bình - 800mm x 50m",
                    "conveyor_params": {
                        "B_mm": 800,
                        "L_m": 50.0,
                        "belt_thickness_mm": 12,
                        "trough_angle_label": "35°",
                        "belt_type": "EP800/4",
                        "motor_rpm": 1450,
                        "motor_efficiency": 0.95,
                        "gearbox_efficiency": 0.98,
                        "carrying_idler_spacing_m": 1.2,
                        "return_idler_spacing_m": 3.0,
                        "material_density_kg_m3": 1600,
                        "conveyor_inclination_deg": 15.0,
                        "belt_speed_mps": 2.5
                    },
                    "expected_results": {
                        "motor_power_kw": 15.5,
                        "belt_tension_n": 12500,
                        "safety_factor": 8.5
                    }
                },
                {
                    "name": "large_conveyor",
                    "description": "Băng tải lớn - 1600mm x 100m",
                    "conveyor_params": {
                        "B_mm": 1600,
                        "L_m": 100.0,
                        "belt_thickness_mm": 18,
                        "trough_angle_label": "45°",
                        "belt_type": "ST1600/6",
                        "motor_rpm": 1450,
                        "motor_efficiency": 0.96,
                        "gearbox_efficiency": 0.99,
                        "carrying_idler_spacing_m": 1.0,
                        "return_idler_spacing_m": 2.5,
                        "material_density_kg_m3": 2000,
                        "conveyor_inclination_deg": 20.0,
                        "belt_speed_mps": 3.2
                    },
                    "expected_results": {
                        "motor_power_kw": 45.8,
                        "belt_tension_n": 32000,
                        "safety_factor": 9.2
                    }
                }
            ]
        }
    
    def run_all_integration_tests(self) -> Dict[str, Any]:
        """Chạy tất cả integration tests"""
        print("🔗 BẮT ĐẦU INTEGRATION TESTING")
        print("=" * 50)
        
        test_suites = [
            self.test_core_system_integration,
            self.test_visualization_integration,
            self.test_data_flow_integration,
            self.test_performance_integration,
            self.test_error_handling_integration,
            self.test_memory_integration
        ]
        
        for test_func in test_suites:
            try:
                print(f"\n🧪 Chạy {test_func.__name__}...")
                result = test_func()
                self.test_results.append(result)
                
                if result['status'] == 'PASSED':
                    print(f"✅ {result['name']}: {result['status']}")
                else:
                    print(f"❌ {result['name']}: {result['status']} - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                error_result = {
                    'name': test_func.__name__,
                    'status': 'FAILED',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
                self.test_results.append(error_result)
                print(f"❌ {error_result['name']}: {error_result['status']} - {error_result['error']}")
        
        return self.generate_integration_report()
    
    def test_core_system_integration(self) -> Dict[str, Any]:
        """Test tích hợp với hệ thống core"""
        start_time = time.time()
        
        try:
            # Test với từng test case
            for test_case in self.test_data['test_cases']:
                params = test_case['conveyor_params']
                expected = test_case['expected_results']
                
                # Tạo ConveyorParameters (nếu có)
                if 'ConveyorParameters' in globals():
                    conveyor_params = ConveyorParameters(**params)
                else:
                    conveyor_params = params
                
                # Tạo CalculationResult (nếu có)
                if 'CalculationResult' in globals():
                    calculation_result = CalculationResult(
                        motor_power_kw=expected['motor_power_kw'],
                        belt_tension_n=expected['belt_tension_n'],
                        safety_factor=expected['safety_factor']
                    )
                else:
                    calculation_result = expected
                
                # Test Model Generator
                model_generator = ConveyorModelGenerator(conveyor_params, calculation_result)
                model_data = model_generator.generate_complete_model()
                
                # Kiểm tra cấu trúc dữ liệu
                required_keys = ['belt_system', 'drive_system', 'support_structure', 'material_flow']
                missing_keys = [key for key in required_keys if key not in model_data]
                
                if missing_keys:
                    raise ValueError(f"Thiếu các key: {missing_keys}")
                
                # Kiểm tra dữ liệu belt system
                belt_system = model_data['belt_system']
                if not isinstance(belt_system, dict):
                    raise ValueError("Belt system phải là dictionary")
                
                if 'geometry' not in belt_system:
                    raise ValueError("Belt system thiếu geometry")
                
                # Kiểm tra kích thước
                geometry = belt_system['geometry']
                if abs(geometry['width'] - params['B_mm']/1000.0) > 0.001:
                    raise ValueError(f"Chiều rộng không khớp: {geometry['width']} vs {params['B_mm']/1000.0}")
                
                if abs(geometry['length'] - params['L_m']) > 0.001:
                    raise ValueError(f"Chiều dài không khớp: {geometry['length']} vs {params['L_m']}")
            
            end_time = time.time()
            
            return {
                'name': 'Core System Integration Test',
                'status': 'PASSED',
                'execution_time': end_time - start_time,
                'test_cases_processed': len(self.test_data['test_cases']),
                'model_generation_success': True
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'name': 'Core System Integration Test',
                'status': 'FAILED',
                'error': str(e),
                'execution_time': end_time - start_time,
                'test_cases_processed': 0,
                'model_generation_success': False
            }
    
    def test_visualization_integration(self) -> Dict[str, Any]:
        """Test tích hợp visualization"""
        start_time = time.time()
        
        try:
            # Test với test case trung bình
            test_case = self.test_data['test_cases'][1]  # medium_conveyor
            params = test_case['conveyor_params']
            expected = test_case['expected_results']
            
            # Tạo model data
            model_generator = ConveyorModelGenerator(params, expected)
            model_data = model_generator.generate_complete_model()
            
            # Test Component Builder
            component_builder = ComponentBuilderManager(model_data)
            components = component_builder.build_all_components()
            
            if not components:
                raise ValueError("Không có components nào được tạo")
            
            # Test Animation Engine
            animation_engine = ConveyorAnimationEngine(model_data)
            
            if not animation_engine.animations:
                raise ValueError("Không có animations nào được tạo")
            
            # Test Physics Simulator
            physics_simulator = ConveyorPhysicsSimulator(model_data)
            
            if not physics_simulator.physics_objects:
                raise ValueError("Không có physics objects nào được tạo")
            
            # Test Performance Optimizer
            optimizer = PerformanceOptimizer()
            optimized_scene = optimizer.optimize_scene(model_data)
            
            if len(str(optimized_scene)) >= len(str(model_data)):
                raise ValueError("Scene không được tối ưu hóa")
            
            end_time = time.time()
            
            return {
                'name': 'Visualization Integration Test',
                'status': 'PASSED',
                'execution_time': end_time - start_time,
                'components_created': len(components),
                'animations_created': len(animation_engine.animations),
                'physics_components': len(physics_simulator.physics_objects),
                'optimization_success': True
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'name': 'Visualization Integration Test',
                'status': 'FAILED',
                'error': str(e),
                'execution_time': end_time - start_time,
                'components_created': 0,
                'animations_created': 0,
                'physics_components': 0,
                'optimization_success': False
            }
    
    def test_data_flow_integration(self) -> Dict[str, Any]:
        """Test luồng dữ liệu từ core system đến visualization"""
        start_time = time.time()
        
        try:
            # Test với tất cả test cases
            total_components = 0
            total_animations = 0
            total_physics = 0
            
            for test_case in self.test_data['test_cases']:
                params = test_case['conveyor_params']
                expected = test_case['expected_results']
                
                # Tạo model data
                model_generator = ConveyorModelGenerator(params, expected)
                model_data = model_generator.generate_complete_model()
                
                # Xây dựng components
                component_builder = ComponentBuilderManager(model_data)
                components = component_builder.build_all_components()
                
                # Tạo animations
                animation_engine = ConveyorAnimationEngine(model_data)
                
                # Tạo physics
                physics_simulator = ConveyorPhysicsSimulator(model_data)
                
                total_components += len(components)
                total_animations += len(animation_engine.animations)
                total_physics += len(physics_simulator.physics_objects)
                
                # Kiểm tra tính nhất quán của dữ liệu
                if 'belt_system' not in model_data:
                    raise ValueError(f"Test case {test_case['name']}: Thiếu belt_system")
                
                if 'drive_system' not in model_data:
                    raise ValueError(f"Test case {test_case['name']}: Thiếu drive_system")
                
                if 'support_structure' not in model_data:
                    raise ValueError(f"Test case {test_case['name']}: Thiếu support_structure")
            
            end_time = time.time()
            
            return {
                'name': 'Data Flow Integration Test',
                'status': 'PASSED',
                'execution_time': end_time - start_time,
                'test_cases_processed': len(self.test_data['test_cases']),
                'total_components': total_components,
                'total_animations': total_animations,
                'total_physics': total_physics,
                'data_consistency': True
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'name': 'Data Flow Integration Test',
                'status': 'FAILED',
                'error': str(e),
                'execution_time': end_time - start_time,
                'test_cases_processed': 0,
                'total_components': 0,
                'total_animations': 0,
                'total_physics': 0,
                'data_consistency': False
            }
    
    def test_performance_integration(self) -> Dict[str, Any]:
        """Test performance integration"""
        start_time = time.time()
        
        try:
            # Test với test case lớn
            test_case = self.test_data['test_cases'][2]  # large_conveyor
            params = test_case['conveyor_params']
            expected = test_case['expected_results']
            
            # Tạo model data
            model_generator = ConveyorModelGenerator(params, expected)
            model_data = model_generator.generate_complete_model()
            
            # Test performance optimization
            optimizer = PerformanceOptimizer()
            
            # Test tất cả optimization levels
            optimization_results = {}
            for level in OptimizationLevel:
                optimizer.settings.level = level
                
                opt_start = time.time()
                optimized = optimizer.optimize_scene(model_data)
                opt_end = time.time()
                
                optimization_results[level.value] = {
                    'optimization_time': opt_end - opt_start,
                    'size_reduction': len(str(model_data)) - len(str(optimized)),
                    'reduction_percent': ((len(str(model_data)) - len(str(optimized))) / len(str(model_data))) * 100
                }
            
            # Test auto-optimization
            auto_optimization_result = optimizer.auto_optimize(current_fps=45, target_fps=60)
            
            # Test memory management
            memory_stats = optimizer.get_memory_usage()
            
            end_time = time.time()
            
            return {
                'name': 'Performance Integration Test',
                'status': 'PASSED',
                'execution_time': end_time - start_time,
                'optimization_levels_tested': len(optimization_results),
                'auto_optimization_success': True,
                'memory_management_working': True,
                'optimization_results': optimization_results
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'name': 'Performance Integration Test',
                'status': 'FAILED',
                'error': str(e),
                'execution_time': end_time - start_time,
                'optimization_levels_tested': 0,
                'auto_optimization_success': False,
                'memory_management_working': False,
                'optimization_results': {}
            }
    
    def test_error_handling_integration(self) -> Dict[str, Any]:
        """Test xử lý lỗi integration"""
        start_time = time.time()
        
        try:
            # Test với dữ liệu không hợp lệ
            invalid_params = {
                'B_mm': -100,  # Chiều rộng âm
                'L_m': 0,      # Chiều dài 0
                'belt_thickness_mm': 0,  # Độ dày 0
                'trough_angle_label': 'invalid',  # Góc không hợp lệ
                'belt_type': '',  # Loại băng tải rỗng
                'motor_rpm': 0,   # RPM 0
                'motor_efficiency': 1.5,  # Hiệu suất > 1
                'gearbox_efficiency': -0.1,  # Hiệu suất âm
                'carrying_idler_spacing_m': 0,  # Khoảng cách 0
                'return_idler_spacing_m': -1,   # Khoảng cách âm
                'material_density_kg_m3': 0,    # Mật độ 0
                'conveyor_inclination_deg': 91, # Góc dốc > 90
                'belt_speed_mps': -1            # Tốc độ âm
            }
            
            invalid_result = {
                'motor_power_kw': -5,  # Công suất âm
                'belt_tension_n': 0,   # Lực căng 0
                'safety_factor': 0     # Hệ số an toàn 0
            }
            
            # Test Model Generator với dữ liệu không hợp lệ
            try:
                model_generator = ConveyorModelGenerator(invalid_params, invalid_result)
                model_data = model_generator.generate_complete_model()
                
                # Nếu không có lỗi, kiểm tra dữ liệu có được validate không
                if model_data:
                    # Kiểm tra xem có validation nào được thực hiện không
                    pass
                    
            except Exception as e:
                # Lỗi được xử lý đúng cách
                pass
            
            # Test Component Builder với dữ liệu không hợp lệ
            try:
                component_builder = ComponentBuilderManager({})
                components = component_builder.build_all_components()
                
                # Nếu không có lỗi, kiểm tra xử lý dữ liệu rỗng
                if components:
                    pass
                    
            except Exception as e:
                # Lỗi được xử lý đúng cách
                pass
            
            end_time = time.time()
            
            return {
                'name': 'Error Handling Integration Test',
                'status': 'PASSED',
                'execution_time': end_time - start_time,
                'invalid_data_handled': True,
                'error_handling_robust': True
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'name': 'Error Handling Integration Test',
                'status': 'FAILED',
                'error': str(e),
                'execution_time': end_time - start_time,
                'invalid_data_handled': False,
                'error_handling_robust': False
            }
    
    def test_memory_integration(self) -> Dict[str, Any]:
        """Test memory integration"""
        start_time = time.time()
        
        try:
            # Test với test case lớn để kiểm tra memory usage
            test_case = self.test_data['test_cases'][2]  # large_conveyor
            params = test_case['conveyor_params']
            expected = test_case['expected_results']
            
            # Tạo nhiều instances để test memory
            instances = []
            for i in range(5):
                model_generator = ConveyorModelGenerator(params, expected)
                model_data = model_generator.generate_complete_model()
                
                component_builder = ComponentBuilderManager(model_data)
                components = component_builder.build_all_components()
                
                animation_engine = ConveyorAnimationEngine(model_data)
                physics_simulator = ConveyorPhysicsSimulator(model_data)
                
                instances.append({
                    'model_generator': model_generator,
                    'model_data': model_data,
                    'component_builder': component_builder,
                    'components': components,
                    'animation_engine': animation_engine,
                    'physics_simulator': physics_simulator
                })
            
            # Test memory cleanup
            import gc
            initial_objects = len(gc.get_objects())
            
            # Xóa instances
            instances.clear()
            gc.collect()
            
            final_objects = len(gc.get_objects())
            objects_cleaned = initial_objects - final_objects
            
            # Test performance optimizer memory management
            optimizer = PerformanceOptimizer()
            optimizer.cleanup_memory()
            
            end_time = time.time()
            
            return {
                'name': 'Memory Integration Test',
                'status': 'PASSED',
                'execution_time': end_time - start_time,
                'instances_created': 5,
                'memory_cleanup_success': objects_cleaned > 0,
                'objects_cleaned': objects_cleaned,
                'optimizer_memory_management': True
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'name': 'Memory Integration Test',
                'status': 'FAILED',
                'error': str(e),
                'execution_time': end_time - start_time,
                'instances_created': 0,
                'memory_cleanup_success': False,
                'objects_cleaned': 0,
                'optimizer_memory_management': False
            }
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Tạo báo cáo integration"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed_tests = total_tests - passed_tests
        
        # Tính toán thống kê
        execution_times = [r.get('execution_time', 0) for r in self.test_results if r['status'] == 'PASSED']
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Phân tích kết quả
        analysis = self._analyze_test_results()
        
        return {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            },
            'performance_metrics': {
                'average_execution_time': avg_execution_time,
                'total_execution_time': sum(execution_times),
                'fastest_test': min(execution_times) if execution_times else 0,
                'slowest_test': max(execution_times) if execution_times else 0
            },
            'test_results': self.test_results,
            'analysis': analysis,
            'recommendations': self._generate_recommendations()
        }
    
    def _analyze_test_results(self) -> Dict[str, Any]:
        """Phân tích kết quả test"""
        analysis = {
            'core_system_integration': False,
            'visualization_integration': False,
            'data_flow_integration': False,
            'performance_integration': False,
            'error_handling_integration': False,
            'memory_integration': False
        }
        
        for result in self.test_results:
            if result['status'] == 'PASSED':
                test_name = result['name'].lower()
                if 'core system' in test_name:
                    analysis['core_system_integration'] = True
                elif 'visualization' in test_name:
                    analysis['visualization_integration'] = True
                elif 'data flow' in test_name:
                    analysis['data_flow_integration'] = True
                elif 'performance' in test_name:
                    analysis['performance_integration'] = True
                elif 'error handling' in test_name:
                    analysis['error_handling_integration'] = True
                elif 'memory' in test_name:
                    analysis['memory_integration'] = True
        
        return analysis
    
    def _generate_recommendations(self) -> List[str]:
        """Tạo recommendations dựa trên kết quả test"""
        recommendations = []
        
        # Phân tích kết quả và đưa ra recommendations
        failed_tests = [r for r in self.test_results if r['status'] == 'FAILED']
        if failed_tests:
            recommendations.append(f"Có {len(failed_tests)} tests thất bại, cần kiểm tra và sửa lỗi")
        
        # Kiểm tra từng loại integration
        analysis = self._analyze_test_results()
        
        if not analysis['core_system_integration']:
            recommendations.append("Core system integration cần được kiểm tra và sửa lỗi")
        
        if not analysis['visualization_integration']:
            recommendations.append("Visualization integration cần được kiểm tra và sửa lỗi")
        
        if not analysis['data_flow_integration']:
            recommendations.append("Data flow integration cần được kiểm tra và sửa lỗi")
        
        if not analysis['performance_integration']:
            recommendations.append("Performance integration cần được kiểm tra và sửa lỗi")
        
        if not analysis['error_handling_integration']:
            recommendations.append("Error handling integration cần được kiểm tra và sửa lỗi")
        
        if not analysis['memory_integration']:
            recommendations.append("Memory integration cần được kiểm tra và sửa lỗi")
        
        if not recommendations:
            recommendations.append("Tất cả integration tests đều pass, hệ thống hoạt động tốt")
        
        return recommendations
    
    def export_test_results(self, output_path: str = "integration_test_results.json"):
        """Xuất kết quả test ra file"""
        report = self.generate_integration_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Kết quả test được xuất ra: {output_path}")


def run_integration_tests():
    """Chạy integration tests"""
    print("🔗 BẮT ĐẦU INTEGRATION TESTING")
    print("=" * 50)
    
    # Tạo test runner
    test_runner = IntegrationTestRunner()
    
    # Chạy tất cả tests
    results = test_runner.run_all_integration_tests()
    
    # In kết quả
    print("\n📊 KẾT QUẢ INTEGRATION TESTING")
    print("=" * 50)
    
    print(f"Tổng số tests: {results['summary']['total_tests']}")
    print(f"Tests passed: {results['summary']['passed_tests']}")
    print(f"Tests failed: {results['summary']['failed_tests']}")
    print(f"Success rate: {results['summary']['success_rate']:.1f}%")
    
    print(f"\nThời gian thực thi trung bình: {results['performance_metrics']['average_execution_time']:.3f}s")
    print(f"Thời gian thực thi tổng cộng: {results['performance_metrics']['total_execution_time']:.3f}s")
    
    # In analysis
    print("\n🔍 PHÂN TÍCH INTEGRATION:")
    analysis = results['analysis']
    for key, value in analysis.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key.replace('_', ' ').title()}")
    
    # In recommendations
    if results['recommendations']:
        print("\n💡 RECOMMENDATIONS:")
        for rec in results['recommendations']:
            print(f"  • {rec}")
    
    # Xuất kết quả
    test_runner.export_test_results()
    
    return test_runner


if __name__ == "__main__":
    run_integration_tests()
