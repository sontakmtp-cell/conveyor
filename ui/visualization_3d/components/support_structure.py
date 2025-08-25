"""
Support Structure Builder - Xây dựng khung đỡ và con lăn 3D
"""

from typing import Dict, Any, List
import math


class SupportStructureBuilder:
    """Xây dựng khung đỡ và con lăn 3D"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.frame_materials = {
            'steel': {'color': 0x34495e, 'roughness': 0.6, 'metalness': 0.8},
            'aluminum': {'color': 0x95a5a6, 'roughness': 0.4, 'metalness': 0.6},
            'galvanized': {'color': 0x7f8c8d, 'roughness': 0.7, 'metalness': 0.7}
        }
        
        self.idler_materials = {
            'steel': {'color': 0x2c3e50, 'roughness': 0.5, 'metalness': 0.9},
            'plastic': {'color': 0xe74c3c, 'roughness': 0.8, 'metalness': 0.1},
            'ceramic': {'color': 0xf39c12, 'roughness': 0.3, 'metalness': 0.2}
        }
    
    def build_carrying_idlers(self) -> List[Dict[str, Any]]:
        """Tạo con lăn mang tải"""
        idler_data = self.data.get('carrying_idlers', {})
        count = idler_data.get('count', 10)
        spacing = idler_data.get('spacing', 1.2)
        diameter = idler_data.get('diameter', 0.133)
        trough_angle = idler_data.get('trough_angle', 20)
        
        idlers = []
        belt_length = self.data.get('belt_system', {}).get('geometry', {}).get('length', 10.0)
        
        for i in range(count):
            # Tính vị trí con lăn
            x_pos = (i / (count - 1)) * belt_length if count > 1 else belt_length / 2
            
            # Tạo con lăn chính
            center_idler = self._create_center_idler(diameter, trough_angle)
            center_idler['position'] = [x_pos, diameter/2, 0]
            
            # Tạo con lăn bên trái
            left_idler = self._create_side_idler(diameter, trough_angle, 'left')
            left_idler['position'] = [x_pos, diameter/2, -0.2]
            
            # Tạo con lăn bên phải
            right_idler = self._create_side_idler(diameter, trough_angle, 'right')
            right_idler['position'] = [x_pos, diameter/2, 0.2]
            
            # Tạo khung đỡ con lăn
            idler_frame = self._create_idler_frame(diameter, trough_angle)
            idler_frame['position'] = [x_pos, 0, 0]
            
            idlers.append({
                'center': center_idler,
                'left': left_idler,
                'right': right_idler,
                'frame': idler_frame,
                'position': x_pos,
                'properties': {
                    'diameter_m': diameter,
                    'trough_angle_deg': trough_angle,
                    'spacing_m': spacing
                }
            })
        
        return idlers
    
    def build_return_idlers(self) -> List[Dict[str, Any]]:
        """Tạo con lăn hồi"""
        idler_data = self.data.get('return_idlers', {})
        count = idler_data.get('count', 8)
        spacing = idler_data.get('spacing', 3.0)
        diameter = idler_data.get('diameter', 0.133)
        
        idlers = []
        belt_length = self.data.get('belt_system', {}).get('geometry', {}).get('length', 10.0)
        
        for i in range(count):
            # Tính vị trí con lăn
            x_pos = (i / (count - 1)) * belt_length if count > 1 else belt_length / 2
            
            # Tạo con lăn hồi (phẳng)
            return_idler = self._create_return_idler(diameter)
            return_idler['position'] = [x_pos, diameter/2, 0]
            
            # Tạo khung đỡ con lăn hồi
            return_frame = self._create_return_frame(diameter)
            return_frame['position'] = [x_pos, 0, 0]
            
            idlers.append({
                'idler': return_idler,
                'frame': return_frame,
                'position': x_pos,
                'properties': {
                    'diameter_m': diameter,
                    'spacing_m': spacing
                }
            })
        
        return idlers
    
    def build_main_frame(self) -> Dict[str, Any]:
        """Tạo khung chính"""
        belt_data = self.data.get('belt_system', {})
        belt_length = belt_data.get('geometry', {}).get('length', 10.0)
        belt_width = belt_data.get('geometry', {}).get('width', 0.5)
        
        # Tính toán kích thước khung
        frame_height = 0.8
        frame_width = belt_width + 0.4
        frame_depth = 0.1
        
        return {
            'type': 'BoxGeometry',
            'parameters': {
                'width': frame_width,
                'height': frame_depth,
                'depth': belt_length
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': self.frame_materials['steel']['color'],
                    'roughness': self.frame_materials['steel']['roughness'],
                    'metalness': self.frame_materials['steel']['metalness']
                }
            },
            'position': [belt_length/2, -frame_depth/2, 0],
            'properties': {
                'dimensions': {
                    'width_m': frame_width,
                    'height_m': frame_depth,
                    'depth_m': belt_length
                },
                'material': 'steel'
            }
        }
    
    def build_legs(self) -> List[Dict[str, Any]]:
        """Tạo chân đỡ"""
        belt_data = self.data.get('belt_system', {})
        belt_length = belt_data.get('geometry', {}).get('length', 10.0)
        belt_width = belt_data.get('geometry', {}).get('width', 0.5)
        
        # Tính toán số chân đỡ
        num_legs = max(3, int(belt_length / 3) + 1)  # Ít nhất 3 chân, mỗi 3m 1 chân
        
        legs = []
        for i in range(num_legs):
            x_pos = (i / (num_legs - 1)) * belt_length if num_legs > 1 else belt_length / 2
            
            leg = {
                'type': 'BoxGeometry',
                'parameters': {
                    'width': 0.1,
                    'height': 0.8,
                    'depth': 0.1
                },
                'material': {
                    'type': 'MeshStandardMaterial',
                    'parameters': {
                        'color': self.frame_materials['steel']['color'],
                        'roughness': self.frame_materials['steel']['roughness'],
                        'metalness': self.frame_materials['steel']['metalness']
                    }
                },
                'position': [x_pos, -0.4, belt_width/2 + 0.1],
                'properties': {
                    'position': x_pos,
                    'height_m': 0.8
                }
            }
            
            legs.append(leg)
        
        return legs
    
    def _create_center_idler(self, diameter: float, trough_angle: float) -> Dict[str, Any]:
        """Tạo con lăn trung tâm"""
        return {
            'type': 'CylinderGeometry',
            'parameters': {
                'radiusTop': diameter / 2,
                'radiusBottom': diameter / 2,
                'height': 0.05,
                'radialSegments': 16
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': self.idler_materials['steel']['color'],
                    'roughness': self.idler_materials['steel']['roughness'],
                    'metalness': self.idler_materials['steel']['metalness']
                }
            }
        }
    
    def _create_side_idler(self, diameter: float, trough_angle: float, side: str) -> Dict[str, Any]:
        """Tạo con lăn bên"""
        # Tính góc nghiêng cho con lăn bên
        angle_rad = math.radians(trough_angle)
        
        return {
            'type': 'CylinderGeometry',
            'parameters': {
                'radiusTop': diameter / 2,
                'radiusBottom': diameter / 2,
                'height': 0.05,
                'radialSegments': 16
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': self.idler_materials['steel']['color'],
                    'roughness': self.idler_materials['steel']['roughness'],
                    'metalness': self.idler_materials['steel']['metalness']
                }
            },
            'rotation': [0, 0, angle_rad if side == 'left' else -angle_rad]
        }
    
    def _create_return_idler(self, diameter: float) -> Dict[str, Any]:
        """Tạo con lăn hồi"""
        return {
            'type': 'CylinderGeometry',
            'parameters': {
                'radiusTop': diameter / 2,
                'radiusBottom': diameter / 2,
                'height': 0.05,
                'radialSegments': 16
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': self.idler_materials['steel']['color'],
                    'roughness': self.idler_materials['steel']['roughness'],
                    'metalness': self.idler_materials['steel']['metalness']
                }
            }
        }
    
    def _create_idler_frame(self, diameter: float, trough_angle: float) -> Dict[str, Any]:
        """Tạo khung đỡ con lăn"""
        # Tính toán kích thước khung đỡ
        frame_width = 0.3
        frame_height = diameter + 0.1
        frame_depth = 0.05
        
        return {
            'type': 'BoxGeometry',
            'parameters': {
                'width': frame_width,
                'height': frame_height,
                'depth': frame_depth
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': self.frame_materials['steel']['color'],
                    'roughness': self.frame_materials['steel']['roughness'],
                    'metalness': self.frame_materials['steel']['metalness']
                }
            }
        }
    
    def _create_return_frame(self, diameter: float) -> Dict[str, Any]:
        """Tạo khung đỡ con lăn hồi"""
        frame_width = 0.3
        frame_height = diameter + 0.1
        frame_depth = 0.05
        
        return {
            'type': 'BoxGeometry',
            'parameters': {
                'width': frame_width,
                'height': frame_height,
                'depth': frame_depth
            },
            'material': {
                'type': 'MeshStandardMaterial',
                'parameters': {
                    'color': self.frame_materials['steel']['color'],
                    'roughness': self.frame_materials['steel']['roughness'],
                    'metalness': self.frame_materials['steel']['metalness']
                }
            }
        }
    
    def build_complete_support_structure(self) -> Dict[str, Any]:
        """Tạo toàn bộ khung đỡ"""
        return {
            'carrying_idlers': self.build_carrying_idlers(),
            'return_idlers': self.build_return_idlers(),
            'main_frame': self.build_main_frame(),
            'legs': self.build_legs(),
            'properties': {
                'total_carrying_idlers': self.data.get('carrying_idlers', {}).get('count', 10),
                'total_return_idlers': self.data.get('return_idlers', {}).get('count', 8),
                'frame_material': 'steel',
                'idler_material': 'steel'
            }
        }

