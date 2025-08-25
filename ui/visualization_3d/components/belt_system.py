"""
Belt System Builder - Xây dựng hệ thống băng tải 3D
"""

from typing import Dict, Any, Optional
import math


class BeltSystemBuilder:
    """Xây dựng hệ thống băng tải 3D"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.belt_materials = {
            'EP': {'color': 0x2c3e50, 'roughness': 0.8, 'metalness': 0.1},
            'ST': {'color': 0x34495e, 'roughness': 0.7, 'metalness': 0.2},
            'NN': {'color': 0x7f8c8d, 'roughness': 0.9, 'metalness': 0.0}
        }
    
    def build_belt_geometry(self) -> Dict[str, Any]:
        """Tạo geometry cho băng tải"""
        geo = self.data.get('geometry', {})
        
        # Tạo băng tải chính với góc trough
        if geo.get('trough_angle', 0) > 0:
            return self._create_troughed_belt(geo)
        else:
            return self._create_flat_belt(geo)
    
    def _create_troughed_belt(self, geo: Dict[str, float]) -> Dict[str, Any]:
        """Tạo băng tải có máng"""
        width = geo.get('width', 0.5)
        length = geo.get('length', 10.0)
        thickness = geo.get('thickness', 0.01)
        trough_angle = math.radians(geo.get('trough_angle', 20))
        
        # Tính toán kích thước máng
        trough_depth = width * math.sin(trough_angle) * 0.3
        center_width = width * 0.6
        
        return {
            'type': 'custom_trough',
            'parameters': {
                'width': width,
                'length': length,
                'thickness': thickness,
                'trough_angle': trough_angle,
                'trough_depth': trough_depth,
                'center_width': center_width
            },
            'vertices': self._generate_trough_vertices(width, length, thickness, trough_angle),
            'faces': self._generate_trough_faces()
        }
    
    def _create_flat_belt(self, geo: Dict[str, float]) -> Dict[str, Any]:
        """Tạo băng tải phẳng"""
        return {
            'type': 'BoxGeometry',
            'parameters': {
                'width': geo.get('width', 0.5),
                'height': geo.get('thickness', 0.01),
                'depth': geo.get('length', 10.0)
            }
        }
    
    def _generate_trough_vertices(self, width: float, length: float, thickness: float, trough_angle: float) -> list:
        """Tạo vertices cho băng tải có máng"""
        vertices = []
        
        # Tạo các điểm theo chiều dài
        segments = max(10, int(length * 2))  # 2 segments per meter
        
        for i in range(segments + 1):
            t = i / segments
            x = t * length
            
            # Điểm trái
            vertices.extend([x, 0, -width/2])
            # Điểm trái trên
            vertices.extend([x, thickness, -width/2])
            # Điểm trái máng
            vertices.extend([x, thickness + thickness * math.sin(trough_angle), -width/2 + thickness * math.cos(trough_angle)])
            
            # Điểm giữa trái
            vertices.extend([x, thickness, -width * 0.2])
            # Điểm giữa
            vertices.extend([x, thickness, 0])
            # Điểm giữa phải
            vertices.extend([x, thickness, width * 0.2])
            
            # Điểm phải máng
            vertices.extend([x, thickness + thickness * math.sin(trough_angle), width/2 - thickness * math.cos(trough_angle)])
            # Điểm phải trên
            vertices.extend([x, thickness, width/2])
            # Điểm phải
            vertices.extend([x, 0, width/2])
        
        return vertices
    
    def _generate_trough_faces(self) -> list:
        """Tạo faces cho băng tải có máng"""
        # Đây là implementation đơn giản, trong thực tế sẽ phức tạp hơn
        return []
    
    def build_belt_material(self) -> Dict[str, Any]:
        """Tạo material cho băng tải"""
        belt_type = self.data.get('material', {}).get('type', 'EP')
        material_props = self.belt_materials.get(belt_type, self.belt_materials['EP'])
        
        return {
            'type': 'MeshStandardMaterial',
            'parameters': {
                'color': material_props['color'],
                'roughness': material_props['roughness'],
                'metalness': material_props['metalness'],
                'transparent': False,
                'opacity': 1.0
            }
        }
    
    def build_belt_texture(self) -> Optional[Dict[str, Any]]:
        """Tạo texture cho băng tải"""
        belt_type = self.data.get('material', {}).get('type', 'EP')
        
        if belt_type == 'EP':
            return {
                'type': 'pattern',
                'pattern': 'diagonal_stripes',
                'scale': 0.1,
                'repeat': [10, 1]
            }
        elif belt_type == 'ST':
            return {
                'type': 'pattern',
                'pattern': 'steel_weave',
                'scale': 0.05,
                'repeat': [20, 1]
            }
        
        return None
    
    def build_complete_belt_system(self) -> Dict[str, Any]:
        """Tạo toàn bộ hệ thống băng tải"""
        return {
            'geometry': self.build_belt_geometry(),
            'material': self.build_belt_material(),
            'texture': self.build_belt_texture(),
            'properties': {
                'width_m': self.data.get('geometry', {}).get('width', 0.5),
                'length_m': self.data.get('geometry', {}).get('length', 10.0),
                'thickness_m': self.data.get('geometry', {}).get('thickness', 0.01),
                'trough_angle_deg': self.data.get('geometry', {}).get('trough_angle', 0),
                'belt_type': self.data.get('material', {}).get('type', 'EP')
            }
        }
