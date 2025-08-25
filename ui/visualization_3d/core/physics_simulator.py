# ui/visualization_3d/core/physics_simulator.py
# -*- coding: utf-8 -*-

"""
Module mô phỏng vật lý cơ bản cho băng tải 3D
"""

import math
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class PhysicsObject:
    """Đối tượng vật lý cơ bản"""
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    acceleration: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    mass: float = 1.0
    friction: float = 0.1
    restitution: float = 0.5


@dataclass
class MaterialParticle(PhysicsObject):
    """Hạt vật liệu trong hệ thống"""
    size: float = 0.01
    material_type: str = "Unknown"
    color: str = "#8B4513"
    lifetime: float = 10.0
    age: float = 0.0


class PhysicsSimulator:
    """Mô phỏng vật lý cơ bản cho băng tải"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.gravity = -9.81  # m/s²
        self.time_step = 1.0 / 60.0  # 60 FPS
        self.particles: List[MaterialParticle] = []
        self.belt_system = None
        self.drive_system = None
        self._setup_physics_world()
    
    def _setup_physics_world(self):
        """Thiết lập thế giới vật lý"""
        # Khởi tạo hệ thống băng tải
        self.belt_system = self._create_belt_physics()
        
        # Khởi tạo hệ thống truyền động
        self.drive_system = self._create_drive_physics()
        
        # Khởi tạo hệ thống con lăn
        self.idler_system = self._create_idler_physics()
    
    def _create_belt_physics(self) -> Dict[str, Any]:
        """Tạo hệ thống vật lý cho băng tải"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        
        return {
            'type': 'belt_physics',
            'width': geometry.get('width', 0.5),
            'length': geometry.get('length', 10.0),
            'trough_angle': geometry.get('trough_angle', 0.0),
            'inclination': geometry.get('inclination', 0.0),
            'friction': 0.3,
            'elasticity': 0.8
        }
    
    def _create_drive_physics(self) -> Dict[str, Any]:
        """Tạo hệ thống vật lý cho truyền động"""
        drive_data = self.data.get('drive_system', {})
        motor_data = drive_data.get('motor', {})
        
        return {
            'type': 'drive_physics',
            'motor_torque': motor_data.get('power_kw', 10.0) * 1000 / motor_data.get('rpm', 1450),
            'gearbox_ratio': drive_data.get('gearbox', {}).get('ratio', 20.0),
            'efficiency': motor_data.get('efficiency', 0.9) * drive_data.get('gearbox', {}).get('efficiency', 0.95),
            'inertia': 0.1
        }
    
    def _create_idler_physics(self) -> Dict[str, Any]:
        """Tạo hệ thống vật lý cho con lăn"""
        support_data = self.data.get('support_structure', {})
        carrying_idlers = support_data.get('carrying_idlers', {})
        
        return {
            'type': 'idler_physics',
            'count': carrying_idlers.get('count', 5),
            'spacing': carrying_idlers.get('spacing', 2.0),
            'diameter': carrying_idlers.get('diameter', 0.108),
            'friction': 0.05,
            'inertia': 0.01
        }
    
    def update_physics(self, delta_time: float):
        """Cập nhật vật lý"""
        # Cập nhật hạt vật liệu
        self._update_particles(delta_time)
        
        # Cập nhật hệ thống băng tải
        self._update_belt_system(delta_time)
        
        # Cập nhật hệ thống truyền động
        self._update_drive_system(delta_time)
        
        # Cập nhật hệ thống con lăn
        self._update_idler_system(delta_time)
    
    def _update_particles(self, delta_time: float):
        """Cập nhật hạt vật liệu"""
        for particle in self.particles[:]:
            # Cập nhật tuổi
            particle.age += delta_time
            
            # Xóa hạt cũ
            if particle.age >= particle.lifetime:
                self.particles.remove(particle)
                continue
            
            # Cập nhật vị trí
            self._update_particle_position(particle, delta_time)
            
            # Kiểm tra va chạm với băng tải
            self._check_belt_collision(particle)
    
    def _update_particle_position(self, particle: MaterialParticle, delta_time: float):
        """Cập nhật vị trí hạt"""
        # Áp dụng trọng lực
        gravity_accel = (0, self.gravity, 0)
        
        # Cập nhật gia tốc
        particle.acceleration = (
            particle.acceleration[0] + gravity_accel[0],
            particle.acceleration[1] + gravity_accel[1],
            particle.acceleration[2] + gravity_accel[2]
        )
        
        # Cập nhật vận tốc
        particle.velocity = (
            particle.velocity[0] + particle.acceleration[0] * delta_time,
            particle.velocity[1] + particle.acceleration[1] * delta_time,
            particle.velocity[2] + particle.acceleration[2] * delta_time
        )
        
        # Áp dụng ma sát
        friction_factor = 1.0 - particle.friction * delta_time
        particle.velocity = (
            particle.velocity[0] * friction_factor,
            particle.velocity[1] * friction_factor,
            particle.velocity[2] * friction_factor
        )
        
        # Cập nhật vị trí
        particle.position = (
            particle.position[0] + particle.velocity[0] * delta_time,
            particle.position[1] + particle.velocity[1] * delta_time,
            particle.position[2] + particle.velocity[2] * delta_time
        )
    
    def _check_belt_collision(self, particle: MaterialParticle):
        """Kiểm tra va chạm với băng tải"""
        belt_data = self.belt_system
        
        # Kiểm tra xem hạt có nằm trên băng tải không
        belt_y = self._calculate_belt_surface_y(particle.position[0], particle.position[2])
        
        if particle.position[1] <= belt_y + particle.size:
            # Hạt chạm băng tải
            particle.position = (particle.position[0], belt_y + particle.size, particle.position[2])
            
            # Áp dụng ma sát băng tải
            belt_friction = belt_data['friction']
            particle.velocity = (
                particle.velocity[0] * (1.0 - belt_friction),
                particle.velocity[1] * 0.1,  # Giảm vận tốc theo trục Y
                particle.velocity[2] * (1.0 - belt_friction)
            )
    
    def _calculate_belt_surface_y(self, x: float, z: float) -> float:
        """Tính độ cao bề mặt băng tải tại vị trí (x, z)"""
        belt_data = self.belt_system
        length = belt_data['length']
        inclination = math.radians(belt_data['inclination'])
        trough_angle = math.radians(belt_data['trough_angle'])
        
        # Tính độ cao dựa trên góc dốc
        base_height = x * math.sin(inclination)
        
        # Tính độ cao dựa trên góc trough (nếu có)
        if trough_angle > 0:
            # Giả sử băng tải có dạng máng
            belt_width = belt_data['width']
            center_offset = abs(z - belt_width / 2)
            trough_depth = belt_width * 0.1 * math.sin(trough_angle)
            trough_height = trough_depth * (center_offset / (belt_width / 2))
            base_height += trough_height
        
        return base_height
    
    def _update_belt_system(self, delta_time: float):
        """Cập nhật hệ thống băng tải"""
        # Logic cập nhật băng tải
        pass
    
    def _update_drive_system(self, delta_time: float):
        """Cập nhật hệ thống truyền động"""
        # Logic cập nhật truyền động
        pass
    
    def _update_idler_system(self, delta_time: float):
        """Cập nhật hệ thống con lăn"""
        # Logic cập nhật con lăn
        pass
    
    def add_material_particle(self, position: Tuple[float, float, float], 
                            material_type: str = "Unknown", size: float = 0.01):
        """Thêm hạt vật liệu mới"""
        particle = MaterialParticle(
            position=position,
            material_type=material_type,
            size=size,
            color=self._get_material_color(material_type)
        )
        self.particles.append(particle)
    
    def get_physics_data(self) -> Dict[str, Any]:
        """Lấy dữ liệu vật lý để truyền vào JavaScript"""
        return {
            'particles': [
                {
                    'position': list(particle.position),
                    'size': particle.size,
                    'color': particle.color,
                    'age': particle.age,
                    'lifetime': particle.lifetime
                }
                for particle in self.particles
            ],
            'belt_system': self.belt_system,
            'drive_system': self.drive_system,
            'idler_system': self.idler_system
        }
    
    def _get_material_color(self, material_type: str) -> str:
        """Lấy màu sắc cho vật liệu"""
        color_map = {
            'Than đá': '#2F4F4F',
            'Sỏi': '#696969',
            'Ngũ cốc': '#DAA520',
            'Dăm gỗ': '#8B4513',
            'Cát khô': '#F4A460',
            'Cát ướt': '#CD853F',
            'Đá mềm': '#708090',
            'Đá vôi': '#F5F5DC',
            'Đất khô': '#8B7355',
            'Đất sét khô': '#654321',
            'Đất sét ướt': '#8B4513',
            'Đất ướt': '#556B2F',
            'Gỗ': '#DEB887',
            'Lúa mạch': '#F0E68C',
            'Muối mỏ': '#F5F5F5',
            'Muối nghiền': '#F8F8FF',
            'Nhôm hạt': '#C0C0C0',
            'Nhôm tán mịn': '#D3D3D3',
            'Quặng đồng': '#CD7F32',
            'Quặng nhôm (Bauxite)': '#F5DEB3',
            'Quặng sắt': '#696969',
            'Than cốc dạng cám': '#2F4F4F',
            'Than cốc tinh': '#1C1C1C',
            'Than mỏ': '#2F4F4F',
            'Xi măng Clinker': '#F5F5DC',
            'Xi măng Portland (khô)': '#F5F5DC'
        }
        return color_map.get(material_type, '#8B4513')
    
    def reset_physics(self):
        """Reset hệ thống vật lý"""
        self.particles.clear()
        self._setup_physics_world()
    
    def set_gravity(self, gravity: float):
        """Thiết lập gia tốc trọng trường"""
        self.gravity = gravity
    
    def set_time_step(self, time_step: float):
        """Thiết lập bước thời gian"""
        self.time_step = max(0.001, min(0.1, time_step))
