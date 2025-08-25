# ui/visualization_3d/core/model_generator.py
# -*- coding: utf-8 -*-

"""
Module tạo mô hình 3D hoàn chỉnh từ tham số tính toán băng tải
"""

import math
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Sử dụng dictionary thay vì import từ core models
from typing import Dict, Any, Optional, Union


@dataclass
class ModelGeometry:
    """Thông tin geometry cho mô hình 3D"""
    width: float
    length: float
    height: float
    thickness: float
    trough_angle: float
    inclination: float


class ConveyorModelGenerator:
    """Tạo mô hình 3D hoàn chỉnh từ tham số tính toán"""
    
    def __init__(self, params: Union[Dict[str, Any], Any], result: Union[Dict[str, Any], Any]):
        self.params = params
        self.result = result
        self.components = {}
        self._validate_inputs()
    
    def _validate_inputs(self):
        """Kiểm tra tính hợp lệ của input"""
        if not self.params:
            raise ValueError("ConveyorParameters không được để trống")
        if not self.result:
            raise ValueError("CalculationResult không được để trống")
    
    def generate_complete_model(self) -> Dict[str, Any]:
        """Tạo mô hình hoàn chỉnh"""
        try:
            model_data = {
                'belt_system': self._generate_belt_system(),
                'drive_system': self._generate_drive_system(),
                'support_structure': self._generate_support_structure(),
                'material_flow': self._generate_material_flow(),
                'safety_features': self._generate_safety_features(),
                'dimensions': self._calculate_dimensions(),
                'materials': self._assign_materials(),
                'metadata': self._generate_metadata()
            }
            
            # Tạo visualization data đơn giản
            viz_data = {
                'belt_dimensions': model_data['belt_system']['geometry'],
                'drive_components': model_data['drive_system'],
                'support_structure': model_data['support_structure'],
                'material_properties': model_data['materials'],
                'animation_settings': self._get_animation_settings(),
                'material_flow': model_data['material_flow']
            }
            
            # Cập nhật result nếu có thể
            if hasattr(self.result, 'visualization_data'):
                self.result.visualization_data = viz_data
            
            return model_data
            
        except Exception as e:
            print(f"Lỗi khi tạo mô hình: {e}")
            return self._generate_fallback_model()
    
    def _generate_belt_system(self) -> Dict[str, Any]:
        """Tạo hệ thống băng tải"""
        # Sử dụng attribute access cho dataclass
        belt_width = getattr(self.params, 'B_mm', 800) / 1000.0  # Chuyển từ mm sang m
        belt_length = getattr(self.params, 'L_m', 50.0)
        belt_thickness = getattr(self.params, 'belt_thickness_mm', 12) / 1000.0
        trough_angle = self._parse_trough_angle(getattr(self.params, 'trough_angle_label', '35°'))
        
        return {
            'geometry': {
                'width': belt_width,
                'length': belt_length,
                'thickness': belt_thickness,
                'trough_angle': trough_angle,
                'cross_section_area': getattr(self.result, 'cross_section_area_m2', 0.5)
            },
            'material': self._get_belt_material(getattr(self.params, 'belt_type', 'EP800/4')),
            'texture': self._generate_belt_texture(),
            'properties': {
                'weight_per_meter': getattr(self.result, 'belt_weight_kgpm', 15.0),
                'tension_max': getattr(self.result, 'max_tension', 10000),
                'speed': getattr(self.result, 'belt_speed_mps', 2.0)
            }
        }
    
    def _generate_drive_system(self) -> Dict[str, Any]:
        """Tạo hệ thống truyền động"""
        if not hasattr(self.result, 'transmission_solution') or not getattr(self.result, 'transmission_solution', None):
            return self._generate_default_drive()
            
        transmission = getattr(self.result, 'transmission_solution', None)
        
        return {
            'motor': {
                'power_kw': getattr(self.result, 'motor_power_kw', 5.5),
                'rpm': getattr(self.params, 'motor_rpm', 1450),
                'efficiency': getattr(self.params, 'motor_efficiency', 0.95)
            },
            'gearbox': {
                'ratio': getattr(transmission, 'gearbox_ratio', 20.0) if transmission else 20.0,
                'efficiency': getattr(self.params, 'gearbox_efficiency', 0.98)
            },
            'chain_drive': {
                'chain_type': getattr(transmission, 'chain_designation', '08A') if transmission else '08A',
                'sprocket_teeth': {
                    'drive': getattr(transmission, 'drive_sprocket_teeth', 20) if transmission else 20,
                    'driven': getattr(transmission, 'driven_sprocket_teeth', 20) if transmission else 20
                },
                'chain_pitch': getattr(transmission, 'chain_pitch_mm', 12.7) / 1000.0 if transmission else 12.7 / 1000.0
            },
            'pulleys': self._generate_pulleys()
        }
    
    def _generate_support_structure(self) -> Dict[str, Any]:
        """Tạo khung đỡ và con lăn"""
        idler_spacing = getattr(self.params, 'carrying_idler_spacing_m', 1.2)
        return_idler_spacing = getattr(self.params, 'return_idler_spacing_m', 3.0)
        
        return {
            'carrying_idlers': {
                'count': max(2, int(getattr(self.params, 'L_m', 50.0) / idler_spacing)),
                'spacing': idler_spacing,
                'diameter': self._calculate_idler_diameter(),
                'trough_angle': self._parse_trough_angle(getattr(self.params, 'trough_angle_label', '35°'))
            },
            'return_idlers': {
                'count': max(2, int(getattr(self.params, 'L_m', 50.0) / return_idler_spacing)),
                'spacing': return_idler_spacing,
                'diameter': self._calculate_idler_diameter() * 0.8
            },
            'frame': self._generate_frame_structure()
        }
    
    def _generate_material_flow(self) -> Dict[str, Any]:
        """Tạo dòng vật liệu"""
        return {
            'material_type': getattr(self.params, 'material', 'coal'),
            'density': getattr(self.params, 'density_tpm3', 1600),
            'particle_size': getattr(self.params, 'particle_size_mm', 25.0),
            'flow_rate': getattr(self.result, 'Qt_tph', 100.0),
            'cross_section': getattr(self.result, 'cross_section_area_m2', 0.5),
            'utilization': getattr(self.result, 'cross_section_utilization_percent', 75.0)
        }
    
    def _generate_safety_features(self) -> Dict[str, Any]:
        """Tạo tính năng an toàn"""
        return {
            'emergency_stop': True,
            'belt_rip_detector': True,
            'overload_protection': True,
            'speed_monitoring': True,
            'temperature_monitoring': True
        }
    
    def _calculate_dimensions(self) -> Dict[str, float]:
        """Tính toán kích thước tổng thể"""
        belt_width = getattr(self.params, 'B_mm', 800) / 1000.0
        belt_length = getattr(self.params, 'L_m', 50.0)
        belt_height = getattr(self.params, 'H_m', 2.0)
        
        # Tính chiều cao thực tế dựa trên góc dốc
        actual_height = belt_length * math.sin(math.radians(getattr(self.params, 'inclination_deg', 0.0)))
        
        return {
            'total_width': belt_width + 0.2,  # Thêm margin cho khung
            'total_length': belt_length + 2.0,  # Thêm margin cho động cơ và đuôi
            'total_height': max(belt_height, actual_height) + 1.0,  # Thêm margin cho khung
            'center_height': belt_height / 2
        }
    
    def _assign_materials(self) -> Dict[str, Any]:
        """Gán vật liệu cho các thành phần"""
        return {
            'belt': {
                            'type': getattr(self.params, 'belt_type', 'EP800/4'),
            'color': self._get_belt_color(getattr(self.params, 'belt_type', 'EP800/4')),
                'texture': 'rubber_pattern'
            },
            'frame': {
                'type': 'steel',
                'color': '#4A4A4A',
                'texture': 'metal_brushed'
            },
            'idlers': {
                'type': 'steel_rubber',
                'color': '#2E2E2E',
                'texture': 'metal_smooth'
            },
            'motor': {
                'type': 'aluminum',
                'color': '#1E90FF',
                'texture': 'metal_polished'
            }
        }
    
    def _generate_metadata(self) -> Dict[str, Any]:
        """Tạo metadata cho mô hình"""
        return {
            'project_name': getattr(self.params, 'project_name', 'Conveyor Project'),
            'designer': getattr(self.params, 'designer', 'Engineering Team'),
            'client': getattr(self.params, 'client', 'Client'),
            'location': getattr(self.params, 'location', 'Factory'),
            'calculation_date': getattr(self.result, 'calculation_date', ''),
            'version': '1.0.0'
        }
    
    def _parse_trough_angle(self, angle_label: str) -> float:
        """Parse góc trough từ label"""
        angle_map = {
            '0° (Phẳng)': 0.0,
            '20°': 20.0,
            '35°': 35.0,
            '45°': 45.0
        }
        return angle_map.get(angle_label, 0.0)
    
    def _get_belt_material(self, belt_type: str) -> Dict[str, Any]:
        """Lấy thông tin vật liệu băng tải"""
        material_map = {
            'Vải EP (Polyester)': {'type': 'fabric_ep', 'strength': 'high'},
            'Vải NN (Nylon)': {'type': 'fabric_nn', 'strength': 'medium'},
            'Dây thép (ST)': {'type': 'steel_cord', 'strength': 'very_high'},
            'PVC': {'type': 'pvc', 'strength': 'low'},
            'Cao su': {'type': 'rubber', 'strength': 'medium'}
        }
        return material_map.get(belt_type, {'type': 'unknown', 'strength': 'medium'})
    
    def _generate_belt_texture(self) -> str:
        """Tạo texture cho băng tải"""
        return 'conveyor_belt_pattern'
    
    def _generate_default_drive(self) -> Dict[str, Any]:
        """Tạo hệ truyền động mặc định"""
        return {
            'motor': {
                'power_kw': getattr(self.result, 'motor_power_kw', 5.5),
                'rpm': 1450,
                'efficiency': 0.9
            },
            'gearbox': {
                'ratio': 20.0,
                'efficiency': 0.95
            },
            'chain_drive': {
                'chain_type': '08A',
                'sprocket_teeth': {'drive': 20, 'driven': 20},
                'chain_pitch': 0.0127
            },
            'pulleys': self._generate_pulleys()
        }
    
    def _generate_pulleys(self) -> Dict[str, Any]:
        """Tạo thông tin puly"""
        return {
            'drive_pulley': {
                'diameter': getattr(self.result, 'drum_diameter_mm', 400) / 1000.0,
                            'width': getattr(self.params, 'B_mm', 800) / 1000.0 + 0.1
        },
        'tail_pulley': {
            'diameter': getattr(self.result, 'drum_diameter_mm', 400) / 1000.0,
            'width': getattr(self.params, 'B_mm', 800) / 1000.0 + 0.1
            }
        }
    
    def _calculate_idler_diameter(self) -> float:
        """Tính đường kính con lăn dựa trên bề rộng băng"""
        belt_width = getattr(self.params, 'B_mm', 800)
        if belt_width <= 500:
            return 0.089  # 89mm
        elif belt_width <= 800:
            return 0.108  # 108mm
        elif belt_width <= 1200:
            return 0.133  # 133mm
        else:
            return 0.159  # 159mm
    
    def _generate_frame_structure(self) -> Dict[str, Any]:
        """Tạo cấu trúc khung"""
        return {
            'type': 'truss',
            'height': getattr(self.params, 'H_m', 2.0) + 1.0,
            'supports': max(3, int(getattr(self.params, 'L_m', 50.0) / 10)),  # Mỗi 10m một trụ đỡ
            'cross_beams': max(2, int(getattr(self.params, 'L_m', 50.0) / 5))  # Mỗi 5m một dầm ngang
        }
    
    def _get_belt_color(self, belt_type: str) -> str:
        """Lấy màu sắc cho băng tải"""
        color_map = {
            'Vải EP (Polyester)': '#8B4513',
            'Vải NN (Nylon)': '#654321',
            'Dây thép (ST)': '#2F4F4F',
            'PVC': '#228B22',
            'Cao su': '#8B4513'
        }
        return color_map.get(belt_type, '#8B4513')
    
    def _get_animation_settings(self) -> Dict[str, Any]:
        """Lấy cài đặt animation"""
        return {
            'belt_speed': getattr(self.result, 'belt_speed_mps', 2.0),
            'material_flow': True,
            'drive_animation': True,
            'idler_rotation': True,
            'playback_speed': 1.0
        }
    
    def _generate_fallback_model(self) -> Dict[str, Any]:
        """Tạo mô hình dự phòng khi có lỗi"""
        return {
            'belt_system': {
                'geometry': {'width': 0.5, 'length': 10.0, 'thickness': 0.01, 'trough_angle': 0.0},
                'material': {'type': 'unknown', 'strength': 'medium'},
                'texture': 'default'
            },
            'drive_system': self._generate_default_drive(),
            'support_structure': {
                'carrying_idlers': {'count': 5, 'spacing': 2.0, 'diameter': 0.108, 'trough_angle': 0.0},
                'return_idlers': {'count': 5, 'spacing': 2.0, 'diameter': 0.089},
                'frame': {'type': 'truss', 'height': 2.0, 'supports': 3, 'cross_beams': 2}
            },
            'material_flow': {'material_type': 'Unknown', 'density': 1.0, 'flow_rate': 100.0},
            'safety_features': {'emergency_stop': True},
            'dimensions': {'total_width': 0.7, 'total_length': 12.0, 'total_height': 3.0, 'center_height': 1.5},
            'materials': {'belt': {'type': 'unknown', 'color': '#8B4513'}},
            'metadata': {'project_name': 'Fallback Model', 'version': '1.0.0'}
        }
