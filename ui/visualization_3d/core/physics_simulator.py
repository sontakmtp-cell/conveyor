"""
Physics Simulator cho băng tải 3D
Mô phỏng vật lý cơ bản của các thành phần
"""

import math
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np


@dataclass
class PhysicsProperties:
    """Thuộc tính vật lý cơ bản"""
    mass_kg: float = 0.0
    density_kg_m3: float = 0.0
    friction_coefficient: float = 0.0
    elasticity: float = 0.0
    damping: float = 0.0


@dataclass
class MaterialProperties:
    """Thuộc tính vật liệu"""
    name: str
    density_kg_m3: float
    friction_coefficient: float
    particle_size_mm: float
    moisture_content_percent: float = 0.0
    angle_of_repose_degrees: float = 30.0
    
    def get_effective_density(self) -> float:
        """Tính toán mật độ hiệu quả dựa trên độ ẩm"""
        if self.moisture_content_percent > 0:
            # Tăng mật độ do độ ẩm
            moisture_factor = 1 + (self.moisture_content_percent / 100) * 0.3
            return self.density_kg_m3 * moisture_factor
        return self.density_kg_m3
    
    def get_angle_of_repose_radians(self) -> float:
        """Chuyển đổi góc nghỉ từ độ sang radian"""
        return math.radians(self.angle_of_repose_degrees)


@dataclass
class BeltPhysics:
    """Vật lý của băng tải"""
    width_m: float
    length_m: float
    thickness_m: float
    material: MaterialProperties
    tension_n: float = 0.0
    speed_mps: float = 0.0
    
    def calculate_mass(self) -> float:
        """Tính khối lượng băng tải"""
        volume = self.width_m * self.length_m * self.thickness_m
        return volume * self.material.density_kg_m3
    
    def calculate_tension_force(self, load_kg: float, incline_degrees: float) -> float:
        """Tính lực căng băng tải"""
        # Lực căng cơ bản
        basic_tension = load_kg * 9.81  # N
        
        # Lực căng do độ dốc
        incline_rad = math.radians(incline_degrees)
        incline_tension = load_kg * 9.81 * math.sin(incline_rad)
        
        # Lực căng do ma sát
        friction_tension = load_kg * 9.81 * math.cos(incline_rad) * self.material.friction_coefficient
        
        total_tension = basic_tension + incline_tension + friction_tension
        self.tension_n = total_tension
        
        return total_tension
    
    def calculate_power_required(self, load_kg: float, incline_degrees: float) -> float:
        """Tính công suất cần thiết"""
        # Lực tổng cộng
        total_force = self.calculate_tension_force(load_kg, incline_degrees)
        
        # Công suất = Lực × Vận tốc
        power_watts = total_force * self.speed_mps
        
        return power_watts / 1000.0  # Chuyển sang kW


@dataclass
class DriveSystemPhysics:
    """Vật lý của hệ truyền động"""
    motor_power_kw: float
    motor_rpm: float
    gearbox_ratio: float
    gearbox_efficiency: float
    chain_efficiency: float
    pulley_diameter_m: float
    
    def calculate_output_torque(self) -> float:
        """Tính mô-men xoắn đầu ra"""
        # Công suất động cơ (W)
        motor_power_w = self.motor_power_kw * 1000
        
        # Tốc độ góc động cơ (rad/s)
        motor_angular_velocity = (self.motor_rpm * 2 * math.pi) / 60
        
        # Mô-men xoắn động cơ
        motor_torque = motor_power_w / motor_angular_velocity
        
        # Mô-men xoắn đầu ra sau hộp số
        output_torque = motor_torque * self.gearbox_ratio * self.gearbox_efficiency
        
        return output_torque
    
    def calculate_belt_tension_capacity(self) -> float:
        """Tính khả năng tạo lực căng của băng tải"""
        output_torque = self.calculate_output_torque()
        
        # Lực căng = Mô-men xoắn / Bán kính pulley
        belt_tension = output_torque / (self.pulley_diameter_m / 2)
        
        return belt_tension
    
    def calculate_chain_tension(self, sprocket_teeth: int, chain_pitch_m: float) -> float:
        """Tính lực căng xích"""
        # Bán kính vòng chia
        pitch_diameter = chain_pitch_m / math.sin(math.pi / sprocket_teeth)
        
        # Lực căng xích
        output_torque = self.calculate_output_torque()
        chain_tension = output_torque / (pitch_diameter / 2)
        
        return chain_tension


@dataclass
class IdlerPhysics:
    """Vật lý của con lăn"""
    diameter_m: float
    length_m: float
    material: MaterialProperties
    bearing_friction: float = 0.01
    rotational_inertia: float = 0.0
    
    def __post_init__(self):
        """Tính toán mô-men quán tính sau khi khởi tạo"""
        # Mô-men quán tính của hình trụ
        radius = self.diameter_m / 2
        volume = math.pi * radius**2 * self.length_m
        mass = volume * self.material.density_kg_m3
        
        # I = (1/2) * m * r² cho hình trụ đặc
        self.rotational_inertia = 0.5 * mass * radius**2
    
    def calculate_rolling_resistance(self, load_n: float) -> float:
        """Tính lực cản lăn"""
        # Lực cản lăn = Hệ số ma sát lăn × Tải trọng
        rolling_resistance = self.bearing_friction * load_n
        return rolling_resistance
    
    def calculate_angular_acceleration(self, torque_nm: float) -> float:
        """Tính gia tốc góc"""
        # α = τ / I
        angular_acceleration = torque_nm / self.rotational_inertia
        return angular_acceleration


@dataclass
class MaterialFlowPhysics:
    """Vật lý của dòng vật liệu"""
    material: MaterialProperties
    flow_rate_tph: float
    belt_width_m: float
    belt_speed_mps: float
    trough_angle_degrees: float
    
    def calculate_cross_sectional_area(self) -> float:
        """Tính diện tích mặt cắt ngang của vật liệu"""
        # Góc máng (radian)
        trough_angle_rad = math.radians(self.trough_angle_degrees)
        
        # Diện tích mặt cắt ngang
        if trough_angle_rad > 0:
            # Máng hình chữ V
            height = (self.belt_width_m / 2) * math.tan(trough_angle_rad)
            area = 0.5 * self.belt_width_m * height
        else:
            # Băng tải phẳng
            height = 0.1  # Chiều cao mặc định
            area = self.belt_width_m * height
        
        return area
    
    def calculate_material_height(self) -> float:
        """Tính chiều cao vật liệu trên băng tải"""
        area = self.calculate_cross_sectional_area()
        
        if self.trough_angle_degrees > 0:
            # Máng hình chữ V
            height = math.sqrt(2 * area / math.tan(math.radians(self.trough_angle_degrees)))
        else:
            # Băng tải phẳng
            height = area / self.belt_width_m
        
        return height
    
    def calculate_actual_flow_rate(self) -> float:
        """Tính lưu lượng thực tế"""
        # Lưu lượng thực tế = Mật độ × Diện tích × Tốc độ
        cross_sectional_area = self.calculate_cross_sectional_area()
        actual_flow_rate = (self.material.density_kg_m3 * cross_sectional_area * 
                           self.belt_speed_mps * 3600) / 1000  # TPH
        
        return actual_flow_rate
    
    def calculate_particle_trajectory(self, time_s: float, initial_position: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Tính quỹ đạo của hạt vật liệu"""
        x0, y0, z0 = initial_position
        
        # Chuyển động theo trục X (theo băng tải)
        x = x0 + self.belt_speed_mps * time_s
        
        # Chuyển động theo trục Y (độ cao)
        # Giả sử hạt dao động nhẹ do rung động
        y = y0 + 0.01 * math.sin(2 * math.pi * 2 * time_s)
        
        # Chuyển động theo trục Z (ngang)
        # Giả sử hạt dao động nhẹ do rung động
        z = z0 + 0.005 * math.sin(2 * math.pi * 1.5 * time_s)
        
        return x, y, z


class ConveyorPhysicsSimulator:
    """Bộ mô phỏng vật lý băng tải"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.physics_objects: Dict[str, Any] = {}
        self.time_step = 0.016  # 60 FPS
        
        # Khởi tạo các đối tượng vật lý
        self._initialize_physics_objects()
    
    def _initialize_physics_objects(self):
        """Khởi tạo các đối tượng vật lý"""
        # Vật liệu mặc định
        default_material = MaterialProperties(
            name="Than đá",
            density_kg_m3=1600,
            friction_coefficient=0.6,
            particle_size_mm=25.0
        )
        
        # Băng tải
        if 'belt_system' in self.data:
            belt_data = self.data['belt_system']
            geometry = belt_data.get('geometry', {})
            
            self.physics_objects['belt'] = BeltPhysics(
                width_m=geometry.get('width', 0.8),
                length_m=geometry.get('length', 10.0),
                thickness_m=geometry.get('thickness', 0.01),
                material=default_material
            )
        
        # Hệ truyền động
        if 'drive_system' in self.data:
            drive_data = self.data['drive_system']
            motor_data = drive_data.get('motor', {})
            gearbox_data = drive_data.get('gearbox', {})
            
            self.physics_objects['drive'] = DriveSystemPhysics(
                motor_power_kw=motor_data.get('power_kw', 5.5),
                motor_rpm=motor_data.get('rpm', 1450),
                gearbox_ratio=gearbox_data.get('ratio', 20.0),
                gearbox_efficiency=gearbox_data.get('efficiency', 0.95),
                chain_efficiency=0.98,
                pulley_diameter_m=0.4
            )
        
        # Con lăn
        if 'support_structure' in self.data:
            support_data = self.data['support_structure']
            idler_data = support_data.get('carrying_idlers', {})
            
            self.physics_objects['idler'] = IdlerPhysics(
                diameter_m=idler_data.get('diameter', 0.15),
                length_m=idler_data.get('length', 0.8),
                material=default_material
            )
        
        # Dòng vật liệu
        if 'material_properties' in self.data:
            material_data = self.data['material_properties']
            
            self.physics_objects['material_flow'] = MaterialFlowPhysics(
                material=default_material,
                flow_rate_tph=material_data.get('flow_rate_tph', 100),
                belt_width_m=self.data.get('belt_system', {}).get('geometry', {}).get('width', 0.8),
                belt_speed_mps=self.data.get('belt_speed_mps', 2.0),
                trough_angle_degrees=self.data.get('belt_system', {}).get('geometry', {}).get('trough_angle', 20)
            )
    
    def simulate_step(self, delta_time: float) -> Dict[str, Any]:
        """Mô phỏng một bước vật lý"""
        simulation_results = {}
        
        # Cập nhật băng tải
        if 'belt' in self.physics_objects:
            belt = self.physics_objects['belt']
            belt.speed_mps = self.data.get('belt_speed_mps', 2.0)
            
            # Tính toán lực căng
            load_kg = self.data.get('material_properties', {}).get('flow_rate_tph', 100) / 3600  # kg/s
            incline_degrees = self.data.get('belt_system', {}).get('geometry', {}).get('inclination', 0)
            
            tension_force = belt.calculate_tension_force(load_kg, incline_degrees)
            power_required = belt.calculate_power_required(load_kg, incline_degrees)
            
            simulation_results['belt'] = {
                'tension_n': tension_force,
                'power_required_kw': power_required,
                'mass_kg': belt.calculate_mass()
            }
        
        # Cập nhật hệ truyền động
        if 'drive' in self.physics_objects:
            drive = self.physics_objects['drive']
            
            output_torque = drive.calculate_output_torque()
            belt_tension_capacity = drive.calculate_belt_tension_capacity()
            
            simulation_results['drive'] = {
                'output_torque_nm': output_torque,
                'belt_tension_capacity_n': belt_tension_capacity,
                'efficiency': drive.gearbox_efficiency * drive.chain_efficiency
            }
        
        # Cập nhật con lăn
        if 'idler' in self.physics_objects:
            idler = self.physics_objects['idler']
            
            # Giả sử tải trọng phân bố đều
            belt_load = self.data.get('material_properties', {}).get('flow_rate_tph', 100) / 3600 * 9.81  # N
            rolling_resistance = idler.calculate_rolling_resistance(belt_load)
            
            simulation_results['idler'] = {
                'rolling_resistance_n': rolling_resistance,
                'rotational_inertia_kgm2': idler.rotational_inertia
            }
        
        # Cập nhật dòng vật liệu
        if 'material_flow' in self.physics_objects:
            material_flow = self.physics_objects['material_flow']
            
            cross_sectional_area = material_flow.calculate_cross_sectional_area()
            material_height = material_flow.calculate_material_height()
            actual_flow_rate = material_flow.calculate_actual_flow_rate()
            
            simulation_results['material_flow'] = {
                'cross_sectional_area_m2': cross_sectional_area,
                'material_height_m': material_height,
                'actual_flow_rate_tph': actual_flow_rate
            }
        
        return simulation_results
    
    def get_physics_summary(self) -> Dict[str, Any]:
        """Lấy tổng quan vật lý"""
        summary = {
            'total_mass_kg': 0.0,
            'total_power_kw': 0.0,
            'efficiency': 0.0,
            'safety_factor': 1.0
        }
        
        # Tính tổng khối lượng
        for obj_name, obj in self.physics_objects.items():
            if hasattr(obj, 'calculate_mass'):
                summary['total_mass_kg'] += obj.calculate_mass()
        
        # Tính tổng công suất
        if 'drive' in self.physics_objects:
            drive = self.physics_objects['drive']
            summary['total_power_kw'] = drive.motor_power_kw
            summary['efficiency'] = drive.gearbox_efficiency * drive.chain_efficiency
        
        # Tính hệ số an toàn
        if 'belt' in self.physics_objects and 'drive' in self.physics_objects:
            belt = self.physics_objects['belt']
            drive = self.physics_objects['drive']
            
            # Hệ số an toàn = Khả năng tải / Tải thực tế
            capacity = drive.calculate_belt_tension_capacity()
            actual_load = belt.tension_n if belt.tension_n > 0 else 1000
            
            if actual_load > 0:
                summary['safety_factor'] = capacity / actual_load
        
        return summary
    
    def export_physics_data(self) -> str:
        """Xuất dữ liệu vật lý dưới dạng JSON"""
        import json
        
        physics_data = {
            'objects': {},
            'simulation': self.simulate_step(self.time_step),
            'summary': self.get_physics_summary()
        }
        
        # Thêm thông tin đối tượng
        for name, obj in self.physics_objects.items():
            physics_data['objects'][name] = {
                'type': obj.__class__.__name__,
                'properties': obj.__dict__
            }
        
        return json.dumps(physics_data, indent=2, default=str)
