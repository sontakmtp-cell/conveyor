# ui/visualization_3d/core/component_builder.py
# -*- coding: utf-8 -*-

"""
Module xây dựng các thành phần riêng lẻ cho visualization 3D
"""

from typing import Dict, Any, List
from abc import ABC, abstractmethod


class ComponentBuilder(ABC):
    """Base class cho việc xây dựng thành phần"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.components = {}
    
    @abstractmethod
    def build(self) -> Dict[str, Any]:
        """Xây dựng thành phần"""
        pass
    
    def get_component(self, name: str) -> Any:
        """Lấy thành phần theo tên"""
        return self.components.get(name)
    
    def add_component(self, name: str, component: Any):
        """Thêm thành phần"""
        self.components[name] = component


class BeltSystemBuilder(ComponentBuilder):
    """Xây dựng hệ thống băng tải 3D"""
    
    def build(self) -> Dict[str, Any]:
        """Tạo geometry cho băng tải"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        
        # Tạo băng tải chính với góc trough
        if geometry.get('trough_angle', 0) > 0:
            belt_geo = self._create_troughed_belt(geometry)
        else:
            belt_geo = self._create_flat_belt(geometry)
        
        # Tạo texture và material
        material = self._create_belt_material(belt_data)
        
        # Tạo animation data
        animation = self._create_belt_animation(belt_data)
        
        return {
            'geometry': belt_geo,
            'material': material,
            'animation': animation,
            'properties': belt_data.get('properties', {})
        }
    
    def _create_troughed_belt(self, geo: Dict[str, float]) -> Dict[str, Any]:
        """Tạo băng tải có máng"""
        # Sử dụng ShapeGeometry để tạo mặt cắt ngang
        # Tạo đường dẫn 3D theo chiều dài
        # Extrude để tạo khối 3D
        
        # Tính toán kích thước máng
        width = geo['width']
        trough_angle = geo['trough_angle']
        depth = width * 0.1  # Độ sâu máng = 10% chiều rộng
        
        # Tạo mặt cắt ngang
        cross_section = {
            'type': 'troughed_shape',
            'width': width,
            'depth': depth,
            'trough_angle': trough_angle,
            'flat_center': width * 0.3,  # 30% chiều rộng ở giữa phẳng
            'side_slopes': trough_angle
        }
        
        # Tạo đường dẫn 3D
        path = {
            'type': 'linear_path',
            'length': geo['length'],
            'inclination': geo.get('inclination', 0)
        }
        
        return {
            'type': 'extruded_shape',
            'cross_section': cross_section,
            'path': path,
            'thickness': geo.get('thickness', 0.01)
        }
    
    def _create_flat_belt(self, geo: Dict[str, float]) -> Dict[str, Any]:
        """Tạo băng tải phẳng"""
        return {
            'type': 'box_geometry',
            'parameters': {
                'width': geo['width'],
                'height': geo.get('thickness', 0.01),
                'depth': geo['length']
            }
        }
    
    def _create_belt_material(self, belt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo material cho băng tải"""
        material_info = belt_data.get('material', {})
        texture = belt_data.get('texture', 'default')
        
        return {
            'type': 'phong_material',
            'color': self._get_belt_color(material_info.get('type', 'unknown')),
            'texture': texture,
            'roughness': 0.8,
            'metalness': 0.1,
            'bump_scale': 0.1
        }
    
    def _create_belt_animation(self, belt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo animation cho băng tải"""
        properties = belt_data.get('properties', {})
        speed = properties.get('speed', 2.0)
        
        return {
            'type': 'belt_movement',
            'speed': speed,
            'texture_offset': self._calculate_texture_offset(speed),
            'material_flow': self._create_material_flow_animation(speed)
        }
    
    def _get_belt_color(self, belt_type: str) -> str:
        """Lấy màu sắc cho băng tải"""
        color_map = {
            'fabric_ep': '#8B4513',
            'fabric_nn': '#654321',
            'steel_cord': '#2F4F4F',
            'pvc': '#228B22',
            'rubber': '#8B4513'
        }
        return color_map.get(belt_type, '#8B4513')
    
    def _calculate_texture_offset(self, speed: float) -> float:
        """Tính offset texture dựa trên tốc độ"""
        return speed * 0.1
    
    def _create_material_flow_animation(self, speed: float) -> Dict[str, Any]:
        """Tạo animation dòng vật liệu"""
        return {
            'type': 'particle_system',
            'particle_count': 100,
            'flow_speed': speed,
            'particle_size': 0.02,
            'color': '#FFA500'
        }


class DriveSystemBuilder(ComponentBuilder):
    """Xây dựng hệ thống truyền động 3D"""
    
    def build(self) -> Dict[str, Any]:
        """Tạo hệ thống truyền động"""
        drive_data = self.data.get('drive_system', {})
        
        components = {}
        
        # Tạo động cơ
        if 'motor' in drive_data:
            components['motor'] = self._create_motor(drive_data['motor'])
        
        # Tạo hộp số
        if 'gearbox' in drive_data:
            components['gearbox'] = self._create_gearbox(drive_data['gearbox'])
        
        # Tạo xích truyền động
        if 'chain_drive' in drive_data:
            components['chain_drive'] = self._create_chain_drive(drive_data['chain_drive'])
        
        # Tạo puly
        if 'pulleys' in drive_data:
            components['pulleys'] = self._create_pulleys(drive_data['pulleys'])
        
        # Tạo animation
        animation = self._create_drive_animation(drive_data)
        
        return {
            'components': components,
            'animation': animation
        }
    
    def _create_motor(self, motor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo động cơ 3D"""
        power = motor_data.get('power_kw', 10.0)
        rpm = motor_data.get('rpm', 1450)
        
        # Tính kích thước động cơ dựa trên công suất
        size_factor = (power / 10.0) ** 0.5  # Căn bậc 2 của tỷ lệ công suất
        
        return {
            'type': 'cylinder_geometry',
            'parameters': {
                'radius': 0.15 * size_factor,
                'height': 0.3 * size_factor
            },
            'material': {
                'type': 'phong_material',
                'color': '#1E90FF',
                'metalness': 0.8,
                'roughness': 0.2
            },
            'properties': {
                'power_kw': power,
                'rpm': rpm,
                'efficiency': motor_data.get('efficiency', 0.9)
            }
        }
    
    def _create_gearbox(self, gearbox_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo hộp số 3D"""
        ratio = gearbox_data.get('ratio', 20.0)
        
        return {
            'type': 'box_geometry',
            'parameters': {
                'width': 0.2,
                'height': 0.25,
                'depth': 0.3
            },
            'material': {
                'type': 'phong_material',
                'color': '#4A4A4A',
                'metalness': 0.9,
                'roughness': 0.1
            },
            'properties': {
                'ratio': ratio,
                'efficiency': gearbox_data.get('efficiency', 0.95)
            }
        }
    
    def _create_chain_drive(self, chain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo xích truyền động 3D"""
        chain_type = chain_data.get('chain_type', '08A')
        sprocket_teeth = chain_data.get('sprocket_teeth', {})
        
        return {
            'type': 'chain_system',
            'chain_type': chain_type,
            'drive_sprocket': {
                'teeth': sprocket_teeth.get('drive', 20),
                'diameter': 0.1
            },
            'driven_sprocket': {
                'teeth': sprocket_teeth.get('driven', 20),
                'diameter': 0.1
            },
            'chain_pitch': chain_data.get('chain_pitch', 0.0127),
            'material': {
                'type': 'phong_material',
                'color': '#2E2E2E',
                'metalness': 0.9,
                'roughness': 0.1
            }
        }
    
    def _create_pulleys(self, pulley_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo puly 3D"""
        drive_pulley = pulley_data.get('drive_pulley', {})
        tail_pulley = pulley_data.get('tail_pulley', {})
        
        return {
            'drive_pulley': self._create_single_pulley(drive_pulley, 'drive'),
            'tail_pulley': self._create_single_pulley(tail_pulley, 'tail')
        }
    
    def _create_single_pulley(self, pulley_info: Dict[str, Any], pulley_type: str) -> Dict[str, Any]:
        """Tạo một puly đơn lẻ"""
        diameter = pulley_info.get('diameter', 0.4)
        width = pulley_info.get('width', 0.6)
        
        return {
            'type': 'cylinder_geometry',
            'parameters': {
                'radius': diameter / 2,
                'height': width
            },
            'material': {
                'type': 'phong_material',
                'color': '#696969',
                'metalness': 0.8,
                'roughness': 0.3
            },
            'properties': {
                'diameter': diameter,
                'width': width,
                'type': pulley_type
            }
        }
    
    def _create_drive_animation(self, drive_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo animation cho hệ truyền động"""
        motor_data = drive_data.get('motor', {})
        gearbox_data = drive_data.get('gearbox', {})
        
        motor_rpm = motor_data.get('rpm', 1450)
        gearbox_ratio = gearbox_data.get('ratio', 20.0)
        
        output_rpm = motor_rpm / gearbox_ratio
        
        return {
            'type': 'rotary_motion',
            'motor_rpm': motor_rpm,
            'output_rpm': output_rpm,
            'pulley_rotation': self._calculate_pulley_rotation(output_rpm)
        }
    
    def _calculate_pulley_rotation(self, rpm: float) -> float:
        """Tính tốc độ quay của puly"""
        return rpm / 60.0  # Chuyển từ RPM sang RPS


class SupportStructureBuilder(ComponentBuilder):
    """Xây dựng khung đỡ và con lăn 3D"""
    
    def build(self) -> Dict[str, Any]:
        """Tạo khung đỡ và con lăn"""
        support_data = self.data.get('support_structure', {})
        
        components = {}
        
        # Tạo con lăn mang
        if 'carrying_idlers' in support_data:
            components['carrying_idlers'] = self._create_carrying_idlers(
                support_data['carrying_idlers']
            )
        
        # Tạo con lăn về
        if 'return_idlers' in support_data:
            components['return_idlers'] = self._create_return_idlers(
                support_data['return_idlers']
            )
        
        # Tạo khung
        if 'frame' in support_data:
            components['frame'] = self._create_frame(support_data['frame'])
        
        # Tạo animation
        animation = self._create_support_animation(support_data)
        
        return {
            'components': components,
            'animation': animation
        }
    
    def _create_carrying_idlers(self, idler_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo con lăn mang"""
        count = idler_data.get('count', 5)
        spacing = idler_data.get('spacing', 2.0)
        diameter = idler_data.get('diameter', 0.108)
        trough_angle = idler_data.get('trough_angle', 0.0)
        
        idlers = []
        for i in range(count):
            position = i * spacing
            idler = self._create_single_idler(diameter, trough_angle, 'carrying')
            idler['position'] = {'x': position, 'y': 0, 'z': 0}
            idlers.append(idler)
        
        return {
            'type': 'idler_group',
            'idlers': idlers,
            'spacing': spacing,
            'trough_angle': trough_angle
        }
    
    def _create_return_idlers(self, idler_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo con lăn về"""
        count = idler_data.get('count', 5)
        spacing = idler_data.get('spacing', 2.0)
        diameter = idler_data.get('diameter', 0.089)
        
        idlers = []
        for i in range(count):
            position = i * spacing
            idler = self._create_single_idler(diameter, 0.0, 'return')
            idler['position'] = {'x': position, 'y': -0.5, 'z': 0}
            idlers.append(idler)
        
        return {
            'type': 'idler_group',
            'idlers': idlers,
            'spacing': spacing,
            'trough_angle': 0.0
        }
    
    def _create_single_idler(self, diameter: float, trough_angle: float, idler_type: str) -> Dict[str, Any]:
        """Tạo một con lăn đơn lẻ"""
        if trough_angle > 0 and idler_type == 'carrying':
            # Con lăn có máng
            return {
                'type': 'troughed_idler',
                'geometry': {
                    'type': 'group_geometry',
                    'center_roller': {
                        'type': 'cylinder_geometry',
                        'parameters': {
                            'radius': diameter / 2,
                            'height': 0.1
                        }
                    },
                    'side_rollers': {
                        'type': 'cylinder_geometry',
                        'parameters': {
                            'radius': diameter / 2 * 0.8,
                            'height': 0.08
                        }
                    },
                    'trough_angle': trough_angle
                },
                'material': {
                    'type': 'phong_material',
                    'color': '#2E2E2E',
                    'metalness': 0.7,
                    'roughness': 0.4
                }
            }
        else:
            # Con lăn phẳng
            return {
                'type': 'flat_idler',
                'geometry': {
                    'type': 'cylinder_geometry',
                    'parameters': {
                        'radius': diameter / 2,
                        'height': 0.1
                    }
                },
                'material': {
                    'type': 'phong_material',
                    'color': '#2E2E2E',
                    'metalness': 0.7,
                    'roughness': 0.4
                }
            }
    
    def _create_frame(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo khung đỡ"""
        frame_type = frame_data.get('type', 'truss')
        height = frame_data.get('height', 2.0)
        supports = frame_data.get('supports', 3)
        cross_beams = frame_data.get('cross_beams', 2)
        
        return {
            'type': frame_type,
            'geometry': {
                'type': 'truss_structure',
                'height': height,
                'supports': supports,
                'cross_beams': cross_beams
            },
            'material': {
                'type': 'phong_material',
                'color': '#4A4A4A',
                'metalness': 0.8,
                'roughness': 0.3
            }
        }
    
    def _create_support_animation(self, support_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo animation cho khung đỡ"""
        return {
            'type': 'idler_rotation',
            'speed': 1.0,
            'rotation_speed': 0.1
        }
