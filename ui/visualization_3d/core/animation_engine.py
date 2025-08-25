"""
Animation Engine cho băng tải 3D
Quản lý animation và chuyển động của các thành phần
"""

import math
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import time


@dataclass
class AnimationState:
    """Trạng thái của animation"""
    is_playing: bool = True
    speed: float = 1.0
    time: float = 0.0
    loop: bool = True
    duration: float = 0.0


@dataclass
class BeltAnimation:
    """Animation cho băng tải"""
    speed_mps: float
    texture_offset: float = 0.0
    material_flow_speed: float = 0.0
    
    def update(self, delta_time: float) -> Dict[str, float]:
        """Cập nhật animation băng tải"""
        # Tính toán offset texture dựa trên tốc độ
        self.texture_offset += self.speed_mps * delta_time * 0.1
        
        # Tính toán tốc độ dòng vật liệu
        self.material_flow_speed = self.speed_mps * 0.8
        
        return {
            'texture_offset': self.texture_offset,
            'material_flow_speed': self.material_flow_speed
        }


@dataclass
class DriveAnimation:
    """Animation cho hệ truyền động"""
    motor_rpm: float
    gearbox_ratio: float
    output_rpm: float = 0.0
    pulley_rotation: float = 0.0
    
    def __post_init__(self):
        """Tính toán tốc độ đầu ra sau khi khởi tạo"""
        self.output_rpm = self.motor_rpm / self.gearbox_ratio
    
    def update(self, delta_time: float) -> Dict[str, float]:
        """Cập nhật animation hệ truyền động"""
        # Tính toán góc quay của pulley
        self.pulley_rotation += self.output_rpm * delta_time * 0.01
        
        return {
            'motor_rpm': self.motor_rpm,
            'output_rpm': self.output_rpm,
            'pulley_rotation': self.pulley_rotation
        }


@dataclass
class IdlerAnimation:
    """Animation cho con lăn"""
    belt_speed_mps: float
    idler_diameter_m: float
    rotation_speed: float = 0.0
    
    def __post_init__(self):
        """Tính toán tốc độ quay của con lăn"""
        if self.idler_diameter_m > 0:
            # v = ω * r, ω = v / r
            self.rotation_speed = self.belt_speed_mps / (self.idler_diameter_m / 2)
    
    def update(self, delta_time: float) -> Dict[str, float]:
        """Cập nhật animation con lăn"""
        return {
            'rotation_speed': self.rotation_speed,
            'angular_velocity': self.rotation_speed * 2 * math.pi
        }


@dataclass
class MaterialFlowAnimation:
    """Animation cho dòng vật liệu"""
    flow_rate_tph: float
    material_density_kg_m3: float
    belt_width_m: float
    belt_speed_mps: float
    particles: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Khởi tạo các hạt vật liệu"""
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Khởi tạo các hạt vật liệu trên băng tải"""
        num_particles = max(10, int(self.flow_rate_tph / 10))
        
        for i in range(num_particles):
            particle = {
                'id': i,
                'x': (i / num_particles) * 10,  # Vị trí X ban đầu
                'y': 0.1,  # Độ cao trên băng tải
                'z': 0,    # Vị trí Z (giữa băng tải)
                'size': 0.05 + (i % 3) * 0.02,  # Kích thước hạt
                'speed': self.belt_speed_mps
            }
            self.particles.append(particle)
    
    def update(self, delta_time: float) -> Dict[str, Any]:
        """Cập nhật animation dòng vật liệu"""
        updated_particles = []
        
        for particle in self.particles:
            # Cập nhật vị trí hạt
            particle['x'] += particle['speed'] * delta_time
            
            # Nếu hạt đi quá chiều dài băng tải, đặt lại ở đầu
            if particle['x'] > 10:
                particle['x'] = 0
            
            updated_particles.append(particle)
        
        self.particles = updated_particles
        
        return {
            'particles': self.particles,
            'flow_rate': self.flow_rate_tph,
            'material_density': self.material_density_kg_m3
        }


class ConveyorAnimationEngine:
    """Quản lý animation và chuyển động của băng tải"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.animations: Dict[str, Any] = {}
        self.state = AnimationState()
        self.start_time = time.time()
        
        # Khởi tạo các animation
        self._initialize_animations()
    
    def _initialize_animations(self):
        """Khởi tạo các animation cơ bản"""
        # Animation cho băng tải
        if 'belt_system' in self.data:
            belt_speed = self.data.get('belt_speed_mps', 2.0)
            self.animations['belt'] = BeltAnimation(belt_speed)
        
        # Animation cho hệ truyền động
        if 'drive_system' in self.data:
            drive_data = self.data['drive_system']
            motor_rpm = drive_data.get('motor', {}).get('rpm', 1450)
            gearbox_ratio = drive_data.get('gearbox', {}).get('ratio', 20.0)
            self.animations['drive'] = DriveAnimation(motor_rpm, gearbox_ratio)
        
        # Animation cho con lăn
        if 'support_structure' in self.data:
            belt_speed = self.data.get('belt_speed_mps', 2.0)
            idler_diameter = 0.15  # Đường kính con lăn mặc định
            self.animations['idler'] = IdlerAnimation(belt_speed, idler_diameter)
        
        # Animation cho dòng vật liệu
        if 'material_properties' in self.data:
            material_data = self.data['material_properties']
            flow_rate = material_data.get('flow_rate_tph', 100)
            density = material_data.get('density_kg_m3', 1600)
            belt_width = self.data.get('belt_system', {}).get('geometry', {}).get('width', 0.8)
            belt_speed = self.data.get('belt_speed_mps', 2.0)
            
            self.animations['material_flow'] = MaterialFlowAnimation(
                flow_rate, density, belt_width, belt_speed
            )
    
    def create_belt_animation(self) -> Dict[str, Any]:
        """Tạo animation cho băng tải"""
        if 'belt' not in self.animations:
            return {}
        
        belt_anim = self.animations['belt']
        return {
            'type': 'belt_movement',
            'speed': belt_anim.speed_mps,
            'texture_offset': belt_anim.texture_offset,
            'material_flow': belt_anim.material_flow_speed
        }
    
    def create_drive_animation(self) -> Dict[str, Any]:
        """Tạo animation cho hệ truyền động"""
        if 'drive' not in self.animations:
            return {}
        
        drive_anim = self.animations['drive']
        return {
            'type': 'rotary_motion',
            'motor_rpm': drive_anim.motor_rpm,
            'output_rpm': drive_anim.output_rpm,
            'pulley_rotation': drive_anim.pulley_rotation
        }
    
    def create_idler_animation(self) -> Dict[str, Any]:
        """Tạo animation cho con lăn"""
        if 'idler' not in self.animations:
            return {}
        
        idler_anim = self.animations['idler']
        return {
            'type': 'idler_rotation',
            'speed': idler_anim.belt_speed_mps,
            'rotation_speed': idler_anim.rotation_speed
        }
    
    def create_material_flow_animation(self) -> Dict[str, Any]:
        """Tạo animation cho dòng vật liệu"""
        if 'material_flow' not in self.animations:
            return {}
        
        material_anim = self.animations['material_flow']
        return {
            'type': 'material_particles',
            'particles': material_anim.particles,
            'flow_rate': material_anim.flow_rate_tph
        }
    
    def update_all_animations(self, delta_time: float) -> Dict[str, Any]:
        """Cập nhật tất cả animation"""
        if not self.state.is_playing:
            return {}
        
        # Cập nhật thời gian
        self.state.time += delta_time * self.state.speed
        
        # Cập nhật từng animation
        updated_animations = {}
        
        for name, animation in self.animations.items():
            if hasattr(animation, 'update'):
                updated_animations[name] = animation.update(delta_time * self.state.speed)
        
        return updated_animations
    
    def play(self):
        """Bắt đầu animation"""
        self.state.is_playing = True
    
    def pause(self):
        """Tạm dừng animation"""
        self.state.is_playing = False
    
    def reset(self):
        """Đặt lại animation"""
        self.state.time = 0.0
        for animation in self.animations.values():
            if hasattr(animation, 'texture_offset'):
                animation.texture_offset = 0.0
            if hasattr(animation, 'pulley_rotation'):
                animation.pulley_rotation = 0.0
    
    def set_speed(self, speed: float):
        """Thiết lập tốc độ animation"""
        self.state.speed = max(0.1, min(5.0, speed))
    
    def get_animation_data(self) -> Dict[str, Any]:
        """Lấy dữ liệu animation hiện tại"""
        return {
            'state': {
                'is_playing': self.state.is_playing,
                'speed': self.state.speed,
                'time': self.state.time
            },
            'animations': {
                'belt': self.create_belt_animation(),
                'drive': self.create_drive_animation(),
                'idler': self.create_idler_animation(),
                'material_flow': self.create_material_flow_animation()
            }
        }
    
    def export_animation_script(self) -> str:
        """Xuất script JavaScript cho animation"""
        script = """
        // Animation Engine Script
        class ConveyorAnimationController {
            constructor() {
                this.animations = {};
                this.isPlaying = true;
                this.speed = 1.0;
                this.clock = new THREE.Clock();
                this.init();
            }
            
            init() {
                this.setupAnimations();
                this.animate();
            }
            
            setupAnimations() {
                // Belt animation
                this.animations.belt = {
                    update: (deltaTime) => {
                        if (this.belt && this.belt.material.map) {
                            this.belt.material.map.offset.x += 0.1 * deltaTime * this.speed;
                        }
                    }
                };
                
                // Drive system animation
                this.animations.drive = {
                    update: (deltaTime) => {
                        if (this.motor) {
                            this.motor.rotation.y += 0.1 * deltaTime * this.speed;
                        }
                        if (this.gearbox) {
                            this.gearbox.rotation.y += 0.05 * deltaTime * this.speed;
                        }
                    }
                };
                
                // Idler animation
                this.animations.idler = {
                    update: (deltaTime) => {
                        if (this.idlers) {
                            this.idlers.forEach(idler => {
                                idler.rotation.z += 0.2 * deltaTime * this.speed;
                            });
                        }
                    }
                };
            }
            
            animate() {
                requestAnimationFrame(() => this.animate());
                
                if (this.isPlaying) {
                    const deltaTime = this.clock.getDelta();
                    
                    Object.values(this.animations).forEach(anim => {
                        if (anim.update) anim.update(deltaTime);
                    });
                }
            }
            
            play() { this.isPlaying = true; }
            pause() { this.isPlaying = false; }
            setSpeed(speed) { this.speed = speed; }
        }
        
        // Khởi tạo controller
        const animationController = new ConveyorAnimationController();
        """
        
        return script
