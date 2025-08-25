# ui/visualization_3d/core/animation_engine.py
# -*- coding: utf-8 -*-

"""
Module quản lý animation và chuyển động của băng tải 3D
"""

import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class AnimationState:
    """Trạng thái animation"""
    is_playing: bool = True
    speed: float = 1.0
    time: float = 0.0
    loop: bool = True


class ConveyorAnimationEngine:
    """Quản lý animation và chuyển động của băng tải"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.animations = {}
        self.state = AnimationState()
        self._setup_animations()
    
    def _setup_animations(self):
        """Thiết lập các animation cơ bản"""
        self.animations = {
            'belt_movement': self.create_belt_animation(),
            'drive_system': self.create_drive_animation(),
            'idler_rotation': self.create_idler_animation(),
            'material_flow': self.create_material_flow_animation(),
            'camera_movement': self.create_camera_animation()
        }
    
    def create_belt_animation(self) -> Dict[str, Any]:
        """Tạo animation cho băng tải"""
        belt_data = self.data.get('belt_system', {})
        properties = belt_data.get('properties', {})
        belt_speed = properties.get('speed', 2.0)
        
        return {
            'type': 'belt_movement',
            'speed': belt_speed,
            'texture_offset': self._calculate_texture_offset(belt_speed)
        }
    
    def create_drive_animation(self) -> Dict[str, Any]:
        """Tạo animation cho hệ truyền động"""
        drive_data = self.data.get('drive_system', {})
        motor_data = drive_data.get('motor', {})
        gearbox_data = drive_data.get('gearbox', {})
        
        motor_rpm = motor_data.get('rpm', 1450)
        gearbox_ratio = gearbox_data.get('ratio', 20.0)
        
        output_rpm = motor_rpm / gearbox_ratio
        
        return {
            'type': 'rotary_motion',
            'motor_rpm': motor_rpm,
            'output_rpm': output_rpm,
            'pulley_rotation': self._calculate_pulley_rotation(output_rpm),
            'update_function': self._update_drive_animation
        }
    
    def create_idler_animation(self) -> Dict[str, Any]:
        """Tạo animation cho con lăn"""
        belt_data = self.data.get('belt_system', {})
        properties = belt_data.get('properties', {})
        belt_speed = properties.get('speed', 2.0)
        
        return {
            'type': 'idler_rotation',
            'speed': belt_speed,
            'rotation_speed': self._calculate_idler_rotation_speed(belt_speed),
            'update_function': self._update_idler_animation
        }
    
    def create_material_flow_animation(self) -> Dict[str, Any]:
        """Tạo animation dòng vật liệu"""
        material_data = self.data.get('material_flow', {})
        flow_rate = material_data.get('flow_rate', 100.0)
        
        return {
            'type': 'particle_system',
            'particle_count': self._calculate_particle_count(flow_rate),
            'flow_speed': self._calculate_flow_speed(flow_rate),
            'particle_size': self._calculate_particle_size(material_data),
            'color': self._get_material_color(material_data.get('material_type', 'Unknown')),
            'update_function': self._update_material_flow_animation
        }
    
    def create_camera_animation(self) -> Dict[str, Any]:
        """Tạo animation camera"""
        return {
            'type': 'camera_movement',
            'presets': self._get_camera_presets(),
            'current_preset': 'Tổng quan',
            'transition_speed': 2.0,
            'update_function': self._update_camera_animation
        }
    
    def update_animations(self, delta_time: float):
        """Cập nhật tất cả animation"""
        if not self.state.is_playing:
            return
        
        # Cập nhật thời gian
        self.state.time += delta_time * self.state.speed
        
        # Cập nhật từng animation
        for anim_name, animation in self.animations.items():
            if 'update_function' in animation:
                animation['update_function'](animation, delta_time)
    
    def play(self):
        """Bắt đầu animation"""
        self.state.is_playing = True
    
    def pause(self):
        """Tạm dừng animation"""
        self.state.is_playing = False
    
    def stop(self):
        """Dừng animation"""
        self.state.is_playing = False
        self.state.time = 0.0
    
    def set_speed(self, speed: float):
        """Thiết lập tốc độ animation"""
        self.state.speed = max(0.1, min(5.0, speed))
    
    def get_animation_data(self) -> Dict[str, Any]:
        """Lấy dữ liệu animation để truyền vào JavaScript"""
        return {
            'state': {
                'is_playing': self.state.is_playing,
                'speed': self.state.speed,
                'time': self.state.time
            },
            'animations': self._prepare_animation_data()
        }
    
    def _prepare_animation_data(self) -> Dict[str, Any]:
        """Chuẩn bị dữ liệu animation cho JavaScript"""
        js_animations = {}
        
        for name, animation in self.animations.items():
            # Loại bỏ update_function vì không thể serialize
            js_animation = {k: v for k, v in animation.items() if k != 'update_function'}
            js_animations[name] = js_animation
        
        return js_animations
    
    def _calculate_texture_offset(self, speed: float) -> float:
        """Tính offset texture dựa trên tốc độ"""
        return speed * 0.1
    
    def _calculate_pulley_rotation(self, rpm: float) -> float:
        """Tính tốc độ quay của puly"""
        return rpm / 60.0  # Chuyển từ RPM sang RPS
    
    def _calculate_idler_rotation_speed(self, belt_speed: float) -> float:
        """Tính tốc độ quay của con lăn"""
        # Tốc độ quay = tốc độ băng / chu vi con lăn
        idler_diameter = 0.108  # Đường kính con lăn mặc định
        circumference = math.pi * idler_diameter
        return belt_speed / circumference
    
    def _calculate_particle_count(self, flow_rate: float) -> int:
        """Tính số lượng particle dựa trên lưu lượng"""
        # Tỷ lệ: 100 TPH = 100 particles
        base_count = 100
        return max(50, min(500, int(flow_rate / 100 * base_count)))
    
    def _calculate_flow_speed(self, flow_rate: float) -> float:
        """Tính tốc độ dòng chảy"""
        # Tỷ lệ: 100 TPH = 1.0 speed
        return max(0.5, min(3.0, flow_rate / 100))
    
    def _calculate_particle_size(self, material_data: Dict[str, Any]) -> float:
        """Tính kích thước particle dựa trên vật liệu"""
        particle_size_mm = material_data.get('particle_size_mm', 10.0)
        # Chuyển từ mm sang m và scale cho phù hợp với scene
        return (particle_size_mm / 1000.0) * 2.0
    
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
    
    def _get_camera_presets(self) -> Dict[str, Dict[str, float]]:
        """Lấy các preset camera"""
        return {
            "Tổng quan": {"x": 10, "y": 15, "z": 20},
            "Hệ truyền động": {"x": 5, "y": 8, "z": 12},
            "Con lăn": {"x": 8, "y": 5, "z": 15},
            "Băng tải": {"x": 15, "y": 10, "z": 8},
            "Tùy chỉnh": {"x": 10, "y": 10, "z": 10}
        }
    
    # Update functions cho từng loại animation
    def _update_belt_animation(self, animation: Dict[str, Any], delta_time: float):
        """Cập nhật animation băng tải"""
        # Logic cập nhật animation băng tải
        pass
    
    def _update_drive_animation(self, animation: Dict[str, Any], delta_time: float):
        """Cập nhật animation hệ truyền động"""
        # Logic cập nhật animation hệ truyền động
        pass
    
    def _update_idler_animation(self, animation: Dict[str, Any], delta_time: float):
        """Cập nhật animation con lăn"""
        # Logic cập nhật animation con lăn
        pass
    
    def _update_material_flow_animation(self, animation: Dict[str, Any], delta_time: float):
        """Cập nhật animation dòng vật liệu"""
        # Logic cập nhật animation dòng vật liệu
        pass
    
    def _update_camera_animation(self, animation: Dict[str, Any], delta_time: float):
        """Cập nhật animation camera"""
        # Logic cập nhật animation camera
        pass
