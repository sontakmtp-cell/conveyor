"""
Drive System Builder - Xây dựng hệ thống truyền động 3D
"""

from typing import Dict, Any, Optional
import math


class DriveSystemBuilder:
    """Xây dựng hệ thống truyền động 3D"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.motor_materials = {
            'standard': {'color': 0x34495e, 'roughness': 0.6, 'metalness': 0.8},
            'premium': {'color': 0x2c3e50, 'roughness': 0.4, 'metalness': 0.9},
            'economy': {'color': 0x7f8c8d, 'roughness': 0.8, 'metalness': 0.6}
        }
        
        self.gearbox_materials = {
            'cast_iron': {'color': 0x2c3e50, 'roughness': 0.7, 'metalness': 0.9},
            'steel': {'color': 0x34495e, 'roughness': 0.5, 'metalness': 0.8}
        }
    
    def build_motor(self) -> Dict[str, Any]:
        """Tạo động cơ 3D"""
        motor_data = self.data.get('motor', {})
        power_kw = motor_data.get('power_kw', 5.5)
        rpm = motor_data.get('rpm', 1450)
        
        # Tính toán kích thước động cơ dựa trên công suất
        motor_diameter = self._calculate_motor_diameter(power_kw)
        motor_length = motor_diameter * 1.5
        
        return {
            'type': 'CylinderGeometry',
            'parameters': {
                'radiusTop': motor_diameter / 2,
                'radiusBottom': motor_diameter / 2,
                'height': motor_length,
                'radialSegments': 16
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': self.motor_materials['standard']['color'],
                    'roughness': self.motor_materials['standard']['roughness'],
                    'metalness': self.motor_materials['standard']['metalness']
                }
            },
            'position': [0, motor_diameter/2, 0],
            'properties': {
                'power_kw': power_kw,
                'rpm': rpm,
                'diameter_m': motor_diameter,
                'length_m': motor_length
            }
        }
    
    def build_gearbox(self) -> Dict[str, Any]:
        """Tạo hộp số 3D"""
        gearbox_data = self.data.get('gearbox', {})
        ratio = gearbox_data.get('ratio', 20.0)
        efficiency = gearbox_data.get('efficiency', 0.95)
        
        # Tính toán kích thước hộp số dựa trên tỷ số truyền
        gearbox_width = 0.3 + ratio * 0.01  # Tăng kích thước theo tỷ số truyền
        gearbox_height = 0.25
        gearbox_depth = 0.4
        
        return {
            'type': 'BoxGeometry',
            'parameters': {
                'width': gearbox_width,
                'height': gearbox_height,
                'depth': gearbox_depth
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': self.gearbox_materials['cast_iron']['color'],
                    'roughness': self.gearbox_materials['cast_iron']['roughness'],
                    'metalness': self.gearbox_materials['cast_iron']['metalness']
                }
            },
            'position': [0, gearbox_height/2, 0.3],
            'properties': {
                'ratio': ratio,
                'efficiency': efficiency,
                'dimensions': {
                    'width_m': gearbox_width,
                    'height_m': gearbox_height,
                    'depth_m': gearbox_depth
                }
            }
        }
    
    def build_chain_drive(self) -> Dict[str, Any]:
        """Tạo xích truyền động 3D"""
        chain_data = self.data.get('chain_drive', {})
        chain_type = chain_data.get('chain_type', '16B')
        drive_teeth = chain_data.get('sprocket_teeth', {}).get('drive', 17)
        driven_teeth = chain_data.get('sprocket_teeth', {}).get('driven', 85)
        chain_pitch = chain_data.get('chain_pitch_mm', 25.4) / 1000.0
        
        # Tính toán kích thước bánh xích
        drive_diameter = self._calculate_sprocket_diameter(drive_teeth, chain_pitch)
        driven_diameter = self._calculate_sprocket_diameter(driven_teeth, chain_pitch)
        
        # Tính toán khoảng cách giữa hai bánh xích
        center_distance = max(drive_diameter, driven_diameter) * 2.5
        
        return {
            'drive_sprocket': {
                'type': 'CylinderGeometry',
                'parameters': {
                    'radiusTop': drive_diameter / 2,
                    'radiusBottom': drive_diameter / 2,
                    'height': 0.05,
                    'radialSegments': drive_teeth
                },
                'material': {
                    'type': 'MeshStandardMaterial',
                    'parameters': {
                        'color': 0x95a5a6,
                        'roughness': 0.6,
                        'metalness': 0.8
                    }
                },
                'position': [0, drive_diameter/2, 0.6],
                'properties': {
                    'teeth': drive_teeth,
                    'diameter_m': drive_diameter,
                    'chain_pitch_m': chain_pitch
                }
            },
            'driven_sprocket': {
                'type': 'CylinderGeometry',
                'parameters': {
                    'radiusTop': driven_diameter / 2,
                    'radiusBottom': driven_diameter / 2,
                    'height': 0.05,
                    'radialSegments': driven_teeth
                },
                'material': {
                    'type': 'MeshStandardMaterial',
                    'parameters': {
                        'color': 0x95a5a6,
                        'roughness': 0.6,
                        'metalness': 0.8
                    }
                },
                'position': [center_distance, driven_diameter/2, 0.6],
                'properties': {
                    'teeth': driven_teeth,
                    'diameter_m': driven_diameter,
                    'chain_pitch_m': chain_pitch
                }
            },
            'chain': self._build_chain_links(center_distance, chain_pitch),
            'properties': {
                'chain_type': chain_type,
                'center_distance_m': center_distance,
                'drive_teeth': drive_teeth,
                'driven_teeth': driven_teeth,
                'chain_pitch_m': chain_pitch
            }
        }
    
    def build_pulleys(self) -> Dict[str, Any]:
        """Tạo pulleys cho băng tải"""
        belt_data = self.data.get('belt_system', {})
        belt_width = belt_data.get('geometry', {}).get('width', 0.5)
        
        # Tính toán kích thước pulleys
        pulley_diameter = belt_width * 0.8
        pulley_width = belt_width + 0.1
        
        return {
            'head_pulley': {
                'type': 'CylinderGeometry',
                'parameters': {
                    'radiusTop': pulley_diameter / 2,
                    'radiusBottom': pulley_diameter / 2,
                    'height': pulley_width,
                    'radialSegments': 24
                },
                'material': {
                    'type': 'MeshStandardMaterial',
                    'parameters': {
                        'color': 0x7f8c8d,
                        'roughness': 0.7,
                        'metalness': 0.8
                    }
                },
                'position': [0, pulley_diameter/2, 0],
                'properties': {
                    'diameter_m': pulley_diameter,
                    'width_m': pulley_width,
                    'type': 'head'
                }
            },
            'tail_pulley': {
                'type': 'CylinderGeometry',
                'parameters': {
                    'radiusTop': pulley_diameter / 2,
                    'radiusBottom': pulley_diameter / 2,
                    'height': pulley_width,
                    'radialSegments': 24
                },
                'material': {
                    'type': 'MeshStandardMaterial',
                    'parameters': {
                        'color': 0x7f8c8d,
                        'roughness': 0.7,
                        'metalness': 0.8
                    }
                },
                'position': [belt_data.get('geometry', {}).get('length', 10.0), pulley_diameter/2, 0],
                'properties': {
                    'diameter_m': pulley_diameter,
                    'width_m': pulley_width,
                    'type': 'tail'
                }
            }
        }
    
    def _calculate_motor_diameter(self, power_kw: float) -> float:
        """Tính toán đường kính động cơ dựa trên công suất"""
        # Công thức đơn giản dựa trên công suất
        if power_kw <= 2.2:
            return 0.15
        elif power_kw <= 5.5:
            return 0.18
        elif power_kw <= 11:
            return 0.22
        elif power_kw <= 22:
            return 0.28
        else:
            return 0.35
    
    def _calculate_sprocket_diameter(self, teeth: int, chain_pitch: float) -> float:
        """Tính toán đường kính bánh xích"""
        # Công thức tính đường kính bánh xích
        return chain_pitch / math.sin(math.pi / teeth)
    
    def _build_chain_links(self, center_distance: float, chain_pitch: float) -> Dict[str, Any]:
        """Tạo các mắt xích"""
        # Tính số mắt xích cần thiết
        num_links = max(10, int(center_distance / chain_pitch) * 2)
        
        return {
            'type': 'chain_links',
            'parameters': {
                'num_links': num_links,
                'link_length': chain_pitch * 0.8,
                'link_width': chain_pitch * 0.3
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': 0x2c3e50,
                    'roughness': 0.8,
                    'metalness': 0.9
                }
            }
        }
    
    def build_complete_drive_system(self) -> Dict[str, Any]:
        """Tạo toàn bộ hệ thống truyền động"""
        return {
            'motor': self.build_motor(),
            'gearbox': self.build_gearbox(),
            'chain_drive': self.build_chain_drive(),
            'pulleys': self.build_pulleys(),
            'properties': {
                'total_ratio': self.data.get('gearbox', {}).get('ratio', 20.0),
                'output_rpm': self.data.get('motor', {}).get('rpm', 1450) / self.data.get('gearbox', {}).get('ratio', 20.0),
                'power_transmission': self.data.get('motor', {}).get('power_kw', 5.5) * self.data.get('gearbox', {}).get('efficiency', 0.95)
            }
        }
